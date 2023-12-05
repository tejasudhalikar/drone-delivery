# Drone Delivery App

This application facilitates the optimization of delivery paths for a drone delivery service. It accepts orders in CSV format and generates an optimal delivery path for a delivery executive to follow.

## Getting Started

This application was developed using Python 3.8 and has been tested on the same version. Currently, there is no user database; however, there is a single hardcoded user - drone_1. To generate a token for this user, use the `/docs` endpoint with the following credentials:
- Username: drone_1
- Password: secret

This will provide a JWT bearer token, which must be attached to all subsequent requests.

### Setup - Development Environment

Follow these steps to run the drone-delivery application:

1. Run the following command:
   ```bash
   uvicorn main:app --reload
   ```
2. Upload orders by attaching a .csv file in the request body using the `/orders/upload` endpoint. A sample orders.csv can be found at `test/orders.csv`
3. Obtain the next delivery path by making a request to the `/orders/next` endpoint.