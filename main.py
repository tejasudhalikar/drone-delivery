import json
from collections import defaultdict
from datetime import datetime, timedelta
from io import BytesIO
from typing import List, Tuple, Union

import aiohttp
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing_extensions import Annotated

from constants import *
from path_optimiser import optimize_path


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

user_coords = defaultdict(list)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(test_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_coordinates(addresses: pd.Series) -> List:
    coords_list = list()
    for address in addresses:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{coord_api}{address}") as resp:
                if resp.status != 200:
                    raise Exception("Invalid address found")
                response = await resp.json()
                coords_list.append(
                    (float(response[0]["lat"]), float(response[0]["lon"]))
                )
    return coords_list


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(test_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/orders/upload")
async def create_upload_file(
    current_user: Annotated[User, Depends(get_current_active_user)], file: UploadFile
):
    contents = await file.read()
    try:
        orders_df = pd.read_csv(BytesIO(contents))
        # Replacing " " with "+" to make addresses compatible with location API
        orders_df["address"] = orders_df["address"].map(lambda x: x.replace(" ", "+"))
        coords_list = await get_coordinates(orders_df["address"])
        print(coords_list)
        optimised_path = await optimize_path(coords_list)
        print(optimised_path)
        globals()["user_coords"][current_user.username] = optimised_path
        print(user_coords)
    except Exception as ex:
        return {"message": "Invalid file uploaded. Please validate."}
    else:
        return {"filename": file.filename}


@app.get("/orders/next")
async def next_node(current_user: Annotated[User, Depends(get_current_active_user)]):
    print(user_coords)
    if user_coords.get(current_user.username, None):
        return {
            "next": json.dumps(globals()["user_coords"][current_user.username].pop(0))
        }
    return {
        "message": "There are no next coordinates. Either you have traversed all or not uploaded path."
    }
