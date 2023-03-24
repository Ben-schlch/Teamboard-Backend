import bcrypt
from typing import Tuple


def hash_and_salt(pw: str) -> Tuple[str, str]:
    salt = bcrypt.gensalt(15)
    # for some reason this function just appends the salt __after__ the password is hashed, rendering it useless
    hashed_pw = bcrypt.hashpw(pw.encode("utf-8") + salt, salt)
    hashed_pw = hashed_pw.decode("utf-8")
    salt = salt.decode("utf-8")
    return salt, hashed_pw


def check_pw(pw: str, salt: str, hashed_pw: str) -> bool:
    salt = salt.encode("utf-8")
    pw = pw.encode("utf-8")
    pw = bcrypt.hashpw(pw + salt, salt)
    hashed_pw = hashed_pw.encode("utf-8")
    return hashed_pw == pw
