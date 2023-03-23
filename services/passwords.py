import bcrypt
from typing import Tuple


def hash_and_salt(pw: str) -> Tuple[str, str]:
    salt = bcrypt.gensalt(15)
    hashed_pw = bcrypt.hashpw(pw.encode("utf-8"), salt)
    hashed_pw = hashed_pw.decode("utf-8")
    salt = salt.decode("utf-8")
    return salt, hashed_pw


def check_pw(hashed_pw: str, salt: str):
    hashed_pw = hashed_pw.encode("utf-8")
    salt = salt.encode("utf-8")
    return bcrypt.checkpw(hashed_pw, salt)
