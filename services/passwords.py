import bcrypt
from typing import Tuple


def hash_and_salt(pw: str) -> str:
    salt = bcrypt.gensalt(12)
    # for some reason this function just appends the salt __after__ the password is hashed, rendering it useless
    hashed_pw = bcrypt.hashpw(pw.encode("utf-8"), salt)
    hashed_pw = hashed_pw.decode("utf-8")
    return hashed_pw


def check_pw(pw: str, hashed_pw: str) -> bool:
    pw = pw.encode("utf-8")
    hashed_pw = hashed_pw.encode("utf-8")
    return bcrypt.checkpw(pw, hashed_pw)
