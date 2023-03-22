from fastapi import FastAPI, Request
from pydantic import BaseModel
from services.register import register_user

app = FastAPI()


class UserBody(BaseModel):
    name: str
    email: str
    pwd: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    print("test123")
    return {"message": f"Hello {name}"}


@app.post("/register/")
async def register(user: UserBody):
    print("aaaaaaaa")
    register_user(**user.dict())
    return user


