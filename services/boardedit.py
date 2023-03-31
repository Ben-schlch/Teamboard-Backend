import psycopg2
import services.db as db


async def teamboardload(email):
    # TODO: Load all teamboards of an user and format them
    return None


async def is_teamboardeditor(teamboardid, email):
    sql = 'SELECT COUNT(1) FROM teamboard_editors WHERE teamboard = %s and editor=%s;'
    values = [teamboardid, email]
    editor = False
    try:
        with db.connect() as con:
            cur = con.cursor()
            cur.execute(sql, values)
            editor = cur.fetchone()
    except psycopg2.DatabaseError as err:
        return False
    if editor:
        return True
    return False


async def teamboardcreate(data, email):
    sql = 'INSERT INTO teamboard (teamboard_name, teamboard_id) VALUES (%s);' \
          'INSERT INTO teamboard_editors (teamboard, editor) VALUES (%s);'  # Note: no quotes
    values = [(data["name"], data["teamboard"]), (data["teamboard"], email)]
    try:
        with db.connect() as con:
            cur = con.cursor()
            cur.execute(sql, values)
    except psycopg2.DatabaseError as err:
        return int(err.pgcode)
    return True


async def teamboarddelete(data, email):
    sql = 'DELETE FROM teamboard where teamboard_id = %s;'
    try:
        with db.connect() as con:
            cur = con.cursor()
            cur.execute(sql, data["teamboard"])
    except psycopg2.DatabaseError as err:
        return int(err.pgcode)
    return True


async def teamboardedit(data, email):
    teamboard_id = data["teamboard"]
    sql = 'UPDATE teamboard set teamboard_name = %s WHERE teamboard_id = %s;'
    values = [data["name"], teamboard_id]
    try:
        with db.connect() as con:
            cur = con.cursor()
            cur.execute(sql, values)
    except psycopg2.DatabaseError as err:
        return int(err.pgcode)
    return True


async def taskcreate(data):
    teamboard_id = data["teamboard"]
    task_id = data["task"]
    task_name = data["name"]

    sql = 'INSERT INTO task (part_of_teamboard, task_id, task_name) VALUES (%s);'
    values = (data["teamboard"], data["task"], data["name"])
    try:
        with db.connect() as con:
            cur = con.cursor()
            cur.execute(sql, values)
    except psycopg2.DatabaseError as err:
        return int(err.pgcode)
    return True


async def taskdelete(data):
    teamboard_id = data["teamboard"]
    task_id = data["task"]
    sql = 'DELETE FROM task where  task_id = %s and part_of_teamboard = %s;'
    try:
        with db.connect() as con:
            cur = con.cursor()
            cur.execute(sql, (task_id, teamboard_id))
    except psycopg2.DatabaseError as err:
        return int(err.pgcode)
    return True


async def taskedit(data):
    teamboard_id = data["teamboard"]
    task_id = data["task"]
    task_name = data["name"]
    sql = 'UPDATE task set task_name = %s WHERE part_of_teamboard = %s and ;'
    values = [data["name"], teamboard_id]
    try:
        with db.connect() as con:
            cur = con.cursor()
            cur.execute(sql, values)
    except psycopg2.DatabaseError as err:
        return int(err.pgcode)
    return True


async def columndelete():
    return None


async def columncreate():
    return None


def columnmove(data):
    return None


def columnedit():
    return None


def subtaskcreate():
    return None


def subtaskedit():
    return None


def subtaskdelete():
    return None


def subtaskmove(data):
    return None
