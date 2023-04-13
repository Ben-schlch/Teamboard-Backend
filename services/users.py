from services.db import connect
from services.passwords import hash_and_salt, check_pw
from services.emails import send_email
from fastapi import HTTPException
from pydantic import BaseModel
from itsdangerous import URLSafeTimedSerializer
import os


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
    salt, pwd = hash_and_salt(pwd)
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO users VALUES (%s, %s, %s, %s)",
                        (email, name, pwd, salt))
            res = cur.statusmessage
    if res:
        # unique violation --> email adr ist bereits in der Datenbank
        if res == 23505:
            raise HTTPException(status_code=409, detail="E-Mail already exists")

    # Send confirmation email
    standard_url = "http://localhost:8080"
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
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT pwd FROM users WHERE mail = %s", (email,))
            res = cur.fetchone()[0]
            return check_pw(pwd, res)


async def gen_confirmation_token(email):
    serializer = URLSafeTimedSerializer(os.getenv("SECRET_TEAMBOARD_KEY"))
    return serializer.dumps(email, salt=os.getenv("SECURITY_TEAMBOARD_PASSWORD_SALT"))


async def confirm_token(token, expiration=1000000):
    serializer = URLSafeTimedSerializer(os.getenv("SECRET_TEAMBOARD_KEY"))
    try:
        email = serializer.loads(
            token,
            salt=os.getenv("SECURITY_TEAMBOARD_PASSWORD_SALT"),
            max_age=expiration
        )
    except:
        return False
    sql = "UPDATE users SET verified = TRUE WHERE mail = %s"
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (email,))
            res = cur.statusmessage
    if res:
        return False
    return True

