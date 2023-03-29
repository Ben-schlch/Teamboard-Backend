from pydantic import BaseModel
from services.users import register_user, login_user
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, WebSocket, Depends, HTTPException, status, WebSocketDisconnect, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import logging
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Secret key used to sign JWT tokens
SECRET_KEY = "mysecretkey"
# Time in minutes before JWT token expires
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# Security scheme to handle JWT tokens
security = HTTPBearer()
# Algorithm to generate the jwt token
ALGORITHM = "HS256"


class UserBody(BaseModel):
    name: str
    email: str
    pwd: str


class Credentials(BaseModel):
    email: str
    pwd: str


# Function to generate JWT token
async def generate_token(email: str, pwd: str):
    if await login_user(email, pwd):
        expiration_time = time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        token = jwt.encode({"sub": email, "exp": expiration_time}, SECRET_KEY, algorithm=ALGORITHM)
        return token
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

async def parse_message(data: dict):
    """Check the message from client"""
    #TODO: JSON Format -->
    return 0

def verify_token(token: str):
    """
    erify a JWT token and return its payload
    @param token:
    @return:
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload["sub"]
        expiration_time = payload.get("exp", None)
        if expiration_time is not None and time.time() > expiration_time:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        return email
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.exceptions.InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature")


async def send_personal_message(message: str, websocket: WebSocket):
    # FIXME: Function or static method in Connection manager?
    await websocket.send_text(message)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

# Define a WebSocket endpoint that requires JWT token authentication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    email = verify_token(token)

    # Handle WebSocket connection
    await manager.connect(websocket)
    await websocket.send_text(f"Welcome, {email}!")
    try:
        while True:
            data = await websocket.receive_text()
            await send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{email} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{email} left the chat")

# Define an HTTP endpoint that generates a JWT token given an email and password
@app.post("/token")
async def get_token(creds: Credentials):
    return {"token": await generate_token(**creds.dict())}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}", status_code=200)
async def say_hello(name: str):
    print("test123")
    return {"message": f"Hello {name}"}


@app.post("/register/")
async def register(user: UserBody):
    print("aaaaaaaa")
    return await register_user(**user.dict())


@app.post("/login/")
async def login(creds: Credentials, response: Response):
    if await login_user(**creds.dict()):
        response.status_code = 200
    else:
        response.status_code = 401
    return {"message": "AAAAAAAAAAA"}

