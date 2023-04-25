import logging
import re
import secrets
import time

import bcrypt
import jwt

from services.db import connect, select_query
from services.passwords import hash_and_salt, check_pw
from services.emails import send_email, send_reset_email
from fastapi import HTTPException
from pydantic import BaseModel
from itsdangerous import URLSafeTimedSerializer
import os
import psycopg.errors


class UserBody(BaseModel):
    name: str
    email: str
    pwd: str


class Credentials(BaseModel):
    email: str
    pwd: str


async def register_user(name: str, email: str, pwd: str):
    """
    Function that adds a user to the database and sends a confirmation email to the user. If the sending of the email
    failed, the user is not added to the database
    :param name: Username of the user (not yet used)
    :param email: Email-address of the user. Test for plausibility is done by sending a confirmation email
    :param pwd: Pw of the user. Will be salted+hashed before saving it in the database.
    :return: Returns nothing, but might raise exceptions.
    """
    # TODO: catch non-valid emails and raise exceptions
    # TODO: look if the email is already in use before sending a confirmation email
    pwd = hash_and_salt(pwd)
    with connect() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("INSERT INTO users VALUES (%s, %s, %s)",
                            (email, name, pwd))
            except psycopg.errors.UniqueViolation:
                raise HTTPException(status_code=409, detail="E-Mail already exists")

    # Send confirmation email
    standard_url = "http://localhost:8000"
    url = os.getenv("TEAMBOARD_URL", standard_url)
    msg = (f"Hello {name},\n"
           f"Thank you for signing up for our service. please confirm your email-adress with this link:"
           f"{url}/confirm/{await gen_confirmation_token(email)}")
    send_email(email, "Confirm your teamboard-adress", msg)


async def login_user(email: str, pwd: str):
    """
    Function that checks the credentials of a user
    :param email: email-address of the user
    :param pwd: Non-hashed password of the user
    :return: True if the credentials are correct, false if they are incorrect or the DBMS returns an error
    """
    # There will be only one result because the mail attribute is the PRIMARY KEY
    res = select_query("SELECT pwd, verified FROM users WHERE mail = %s", (email,))
    if not res:
        return False
    res = res[0]
    return check_pw(pwd, res["pwd"]) and res["verified"]


async def gen_confirmation_token(email):
    serializer = URLSafeTimedSerializer(os.getenv("SECRET_TEAMBOARD_KEY", "aaa"))
    return serializer.dumps(email, salt=os.getenv("SECURITY_TEAMBOARD_PASSWORD_SALT", "bbb"))


async def confirm_token(token, expiration=1000000):
    serializer = URLSafeTimedSerializer(os.getenv("SECRET_TEAMBOARD_KEY", "aaa"))
    try:
        email = serializer.loads(
            token,
            salt=os.getenv("SECURITY_TEAMBOARD_PASSWORD_SALT", "bbb"),
            max_age=expiration
        )
    except:
        return False
    sql = "UPDATE users SET verified = TRUE WHERE mail = %s"
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (email,))
            res = cur.rowcount
    if not res:
        return False
    return True


SECRET_KEY = os.getenv("SECRET_RESET_KEY", "secret_key")
# Time in minutes before JWT token expires
ACCESS_TOKEN_EXPIRE_MINUTES = 60
# Algorithm to generate the jwt token
ALGORITHM = "HS256"


async def send_reset_token(email: str):
    """
    Send a reset token to the user
    @param email:
    @return:
    """
    # check if the email exists
    sql = "SELECT count(1) FROM users WHERE mail = %s"
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (email,))
            res = cur.fetchone()
    if not res:
        return False

    token = await generate_reset_token()

    await send_reset_email(email, token)

    salt = bcrypt.gensalt()
    token = bcrypt.hashpw(token.encode("utf-8"), salt)
    token = token.decode("utf-8")
    sql = "UPDATE users SET reset_token = %s WHERE mail = %s"
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (token, email))


async def generate_reset_token():
    random_string = secrets.token_hex(64)
    expiration_time = time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    token = jwt.encode({"token": random_string, "exp": expiration_time}, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def verify_reset_token(email: str, token: str):
    """
    Verify the reset token
    :param email:
    :param token:
    :return:
    """
    logging.info(f"Verifying token for {email}")
    try:
        sql = "SELECT reset_token FROM users WHERE mail = %s"
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (email,))
                res = cur.fetchone()
        print(res)
        if not res:
            return False
        res = res[0]
        if not bcrypt.checkpw(token.encode("utf-8"), res.encode("utf-8")):
            logging.debug("Token not valid")
            return False
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        if time.time() > exp:
            logging.warning("Token expired")
            return False

        sql = "UPDATE users SET reset_token = NULL WHERE mail = %s"
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (email,))

        return True
    except Exception as e:
        logging.warning("Exception: " + str(e))
        return False


async def reset_password(email: str, password: str):
    """
    Reset the password of a user
    @param email:
    @param password:
    @return:
    """
    password = hash_and_salt(password)
    sql = "UPDATE users SET pwd = %s WHERE mail = %s"
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (password, email))


async def check_password_complexity(password: str):
    """
    Check if the password is complex enough
    Needs at least 8 characters, one uppercase and one lowercase letter and one number
    @param password:
    @return:
    """
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    return True
