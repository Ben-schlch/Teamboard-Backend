from services.dbconnection import connect
from services.passwords import hash_and_salt, check_pw


def register_user(name, email, pwd, profilepicture=None):
    conn, cur = connect()
    sql = f"INSERT INTO users (username, mail, pwd, verified, profilepicture) " \
          f"VALUES ('{name}', '{email}', '{pwd}', 'false', '{profilepicture}')"
    cur.execute(sql)
    resp = cur.fetchall()
    print(resp)

