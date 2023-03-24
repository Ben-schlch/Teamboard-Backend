from fastapi import FastAPI, WebSocket, Response
from pydantic import BaseModel
from services.users import register_user, login_user

app = FastAPI()


class UserBody(BaseModel):
    name: str
    email: str
    pwd: str


class Credentials(BaseModel):
    email: str
    pwd: str


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


@app.websocket("/ws/")
async def websocket(ws: WebSocket):
    await ws.accept()
    logged_in = False
    while not logged_in:
        creds = await ws.receive_json()
        logged_in = await login_user(**creds.dict())
