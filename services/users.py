from services.db import insert_query, select_query
from services.passwords import hash_and_salt, check_pw
from services.emails import send_email
from fastapi import HTTPException
from pydantic import BaseModel


class UserBody(BaseModel):
    name: str
    email: str
    pwd: str


class Credentials(BaseModel):
    email: str
    pwd: str


async def register_user(name, email, pwd):
    salt, pwd = hash_and_salt(pwd)
    res = insert_query("users",
                       ['username', 'mail', 'pwd', 'salt'],
                       [name, email, pwd, salt])
    if res:
        # unique violation --> email adr ist bereits in der Datenbank
        if res == 23505:
            raise HTTPException(status_code=409, detail="E-Mail already exists")

    msg = f"""Hello {name},
    Thank you for signing up for our service. please confirm your email-adress with this link:"""
    send_email(email, "Confirm your teamboard-adress", msg)


async def login_user(email: str, pwd: str):
    # There will be only one result because the mail attribute is the PRIMARY KEY
    try:
        res = select_query("users", ["pwd"], f"mail = '{email}'")[0]
    except IndexError:
        return False
    if type(res) is int:
        return False
    return check_pw(pwd, res["pwd"])
