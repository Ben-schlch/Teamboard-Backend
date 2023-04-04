import logging

from fastapi import WebSocket, HTTPException, status
import jwt
from services.users import login_user
from services.db import connect
import time

# Secret key used to sign JWT tokens
SECRET_KEY = "mysecretkey"
# Time in minutes before JWT token expires
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# Algorithm to generate the jwt token
ALGORITHM = "HS256"


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[(WebSocket, str)] = []

    async def connect(self, websocket: WebSocket, email: str):
        await websocket.accept()
        self.active_connections.append((websocket, email))

    def disconnect(self, websocket: WebSocket):
        item = [item for item in self.active_connections if item[0] == websocket][0]
        self.active_connections.remove(item)

    async def broadcast(self, message: str, teamboard: int):
        logging.info(f"Broadcasting message to teamboard {teamboard}")
        with connect() as conn:
            with conn.cursor() as cur:
                sql = "SELECT editor FROM teamboard_editors WHERE teamboard = %s"
                cur.execute(sql, teamboard)
                editors = cur.fetchall()
                editors = [item[0] for item in editors]
        for connection in [item[0] for item in self.active_connections if item[1] in editors]:
            await connection.send_text(message)

    @staticmethod
    async def send_personal_message(message: str, websocket: WebSocket):
        logging.info(f"Sending personal message '{message}' to {websocket}")
        await websocket.send_text(message)


# Function to generate JWT token
async def generate_token(email: str, pwd: str):
    if await login_user(email, pwd):
        expiration_time = time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        token = jwt.encode({"sub": email, "exp": expiration_time}, SECRET_KEY, algorithm=ALGORITHM)
        return token
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")


def verify_token(token: str):
    """
    verify a JWT token and return its payload
    @param token:
    @return:
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        email = payload["sub"]
        expiration_time = payload.get("exp", None)
        if expiration_time is not None and time.time() > expiration_time:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        return email
    except jwt.exceptions.InvalidSignatureError as e:
        logging.warning("Invalid token signature", e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature")
    except jwt.exceptions.DecodeError as e:
        logging.warning("Invalid token", e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
