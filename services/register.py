from services.dbconnection import connect
from services.passwords import hash_and_salt, check_pw
from services.emails import send_email


def register_user(name, email, pwd, profilepicture=None):
    salt, pwd = hash_and_salt(pwd)
    conn, cur = connect()
    sql = f"INSERT INTO users (username, mail, pwd, salt, verified, profilepicture) " \
          f"VALUES ('{name}', '{email}', '{pwd}', '{salt}', 'false', '{profilepicture}')"
    cur.execute(sql)
    msg = f"""Hello {name},
    Thank you for signing up for our service. please confirm your email-adress with this link:"""
    send_email(email, "Confirm your teamboard-adress", msg)

