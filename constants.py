from collections import defaultdict

coord_api = "https://nominatim.openstreetmap.org/search?format=json&q="
SECRET_KEY = "517152cf4de6157130db2684fb15dab84e6c95774bcc170fc583931e4c193c0f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

test_users_db = {
    "drone_1": {
        "username": "drone_1",
        "full_name": "drone 1",
        "email": "drone_1@pizza.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

user_coords = defaultdict(list)

pizza_shop_coords = (36.0, -120.0)
