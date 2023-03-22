import bcrypt


def hash_and_salt(pw: str):
    salt = bcrypt.gensalt(15)
    hashed_pw = bcrypt.hashpw(pw.encode("utf-8"), salt)
    return salt, hashed_pw


def check_pw(hashed_pw, salt):
    return bcrypt.checkpw(hashed_pw, salt)
