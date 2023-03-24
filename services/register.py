from services.db import insert_query, select_query
from services.passwords import hash_and_salt, check_pw
from services.emails import send_email
import psycopg2


async def register_user(name, email, pwd, profilepicture=None):
    salt, pwd = hash_and_salt(pwd)
    res = insert_query("users",
                 ['username', 'mail', 'pwd', 'salt', 'verified', 'profilepicture'],
                 [name, email, pwd, salt, False, profilepicture])
    if res:
        # unique violation --> email adr ist bereits in der Datenbank
        if res == 23505:
            return {"message": "Die e-mail Adresse wird bereits verwendet"}
    msg = f"""Hello {name},
    Thank you for signing up for our service. please confirm your email-adress with this link:"""
    send_email(email, "Confirm your teamboard-adress", msg)
    return 200


async def login_user(email: str, pwd: str):
    # There will be only one result because the mail attribute is the PRIMARY KEY
    res = select_query("users", ["pwd", "salt"], f"mail = '{email}'")[0]
    if type(res) is int:
        return res
    if check_pw(pwd, res["salt"], res["pwd"]):
        return 200


