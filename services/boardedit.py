import psycopg
import services.db as db
import services.positioncalc as positioncalc


async def teamboardload(email):
    # TODO: Load all teamboards of an user and format them
    return None


async def is_teamboardeditor(teamboardid, email):
    sql = 'SELECT COUNT(1) FROM teamboard_editors WHERE teamboard = %s and editor=%s;'
    values = [teamboardid, email]
    editor = False
    with db.connect() as con:
        cur = con.cursor()
        cur.execute(sql, values)
        editor = cur.fetchone()
        editor = editor[0] > 0  # Convert to boolean
    return editor


async def teamboardcreate(data, email):
    sql = 'INSERT INTO teamboard (teamboard_name, teamboard_id) VALUES (%s);' \
          'INSERT INTO teamboard_editors (teamboard, editor) VALUES (%s);'  # Note: no quotes
    values = [(data["name"], data["teamboard"]), (data["teamboard"], email)]
    try:
        with db.connect() as con:
            cur = con.cursor()
            cur.execute(sql, values)
    except psycopg.DatabaseError as err:
        return int(err.pgcode)
    return True


async def teamboarddelete(data):
    sql = 'DELETE FROM teamboard where teamboard_id = %s;'
    try:
        with db.connect() as con:
            cur = con.cursor()
            cur.execute(sql, data["teamboard"])
    except psycopg.DatabaseError as err:
        return int(err.pgcode)
    return True


async def teamboardedit(data):
    teamboard_id = data["teamboard"]
    sql = 'UPDATE teamboard set teamboard_name = %s WHERE teamboard_id = %s;'
    values = [data["name"], teamboard_id]
    try:
        with db.connect() as con:
            cur = con.cursor()
            cur.execute(sql, values)
    except psycopg.DatabaseError as err:
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
    except psycopg.DatabaseError as err:
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
    except psycopg.DatabaseError as err:
        return int(err.pgcode)
    return True


async def taskedit(data):
    teamboard_id = data["teamboard"]
    task_id = data["task"]
    task_name = data["name"]
    sql = 'UPDATE task set task_name = %s WHERE part_of_teamboard = %s and task_id = %s;'
    values = [task_name, teamboard_id, task_id]
    try:
        with db.connect() as con:
            cur = con.cursor()
            cur.execute(sql, values)
    except psycopg.DatabaseError as err:
        return int(err.pgcode)
    return True


async def columndelete(data: dict):
    teamboard_id = data["teamboard"]
    task_id = data["task"]
    colum_id = data["column"]

    try:
        with db.connect() as con:
            cur = con.cursor()
            sql = "SELECT column_id FROM task_column " \
                  "WHERE part_of_teamboard=%s AND part_of_task=%s and r_neighbor=%s;"
            cur.execute(sql, (teamboard_id, task_id, colum_id))
            left_neighbor = cur.fetchone()
            left_neighbor = left_neighbor[0]
            sql = "SELECT column_id FROM task_column " \
                  "WHERE part_of_teamboard=%s AND part_of_task=%s and l_neighbor=%s;"
            cur.execute(sql, (teamboard_id, task_id, colum_id))
            right_neighbor = cur.fetchone()
            right_neighbor = right_neighbor[0]
            sql = 'UPDATE task_column SET r_neighbor = %s ' \
                  'WHERE part_of_teamboard = %s and part_of_task = %s and column_id = %s;' \
                  'UPDATE task_column SET l_neighbor = %s ' \
                  'WHERE part_of_teamboard = %s and part_of_task = %s and column_id = %s;' \
                  'DELETE FROM task_column where  column_id = %s and part_of_task = %s and part_of_teamboard = %s;'
            cur.execute(sql, (right_neighbor, teamboard_id, task_id, left_neighbor,
                              left_neighbor, teamboard_id, task_id, right_neighbor,
                              colum_id, task_id, teamboard_id))
    except psycopg.DatabaseError as err:
        return int(err.pgcode)
    return True


async def columncreate(data):
    teamboard_id = data["teamboard"]
    task_id = data["task"]
    column_name = data["name"]
    sql = 'SELECT column_id FROM task_column WHERE part_of_teamboard=%s AND part_of_task=%s and r_neighbor IS NULL;'
    values = (teamboard_id, task_id)
    with db.connect() as con:
        cur = con.cursor()
        cur.execute(sql, values)
        column_id = cur.fetchone()
        column_id = column_id[0]
        sql = 'INSERT INTO task_column (part_of_teamboard, part_of_task, name_of_column, l_neighbor) ' \
              'VALUES (%s) RETURNING column_id;'
        values = (teamboard_id, task_id, column_name, column_id)
        cur.execute(sql, values)
        new_column_id = cur.fetchone()
        new_column_id = column_id[0]
        sql = 'UPDATE task_column SET r_neighbor = %s ' \
              'Where part_of_teamboard=%s AND part_of_task=%s and column_id= %s and r_neighbor IS NULL;'
        values = (new_column_id, teamboard_id, task_id, column_id)
        cur.execute(sql, values)
        print("Test: ID: ", new_column_id)
    return new_column_id


def columnmove(data):
    teamboard_id = data["teamboard"]
    task_id = data["task"]
    colum_id = data["column"]
    newposition = data["newPosition"]
    return positioncalc.move_column(teamboard_id, task_id, colum_id, newposition)


async def columnedit(data):
    teamboard_id = data["teamboard"]
    task_id = data["task"]
    column_id = data["column"]
    name = data["name"]
    sql = 'UPDATE task_column set name_of_column = %s ' \
          'WHERE part_of_teamboard = %s and part_of_task = %s and column_id = %s;'
    values = [name, teamboard_id, task_id, column_id]
    with db.connect() as con:
        cur = con.cursor()
        cur.execute(sql, values)


async def subtaskcreate(data):
    max_columns = {"created", "deadline", "description", "color", "priority", "worker", "position"}
    columns = max_columns.intersection(data.keys())
    with db.connect() as con:
        cur = con.cursor()
        sql = 'SELECT subtask_id FROM subtask WHERE part_of_teamboard=%s ' \
              'AND part_of_task=%s and part_of_column=%s and r_neighbor IS NULL;'
        values = (data["teamboard"], data["task"], data["column"])
        cur.execute(sql, values)
        neighbor = cur.fetchone()[0]

        insert = [data[x] for x in columns]
        insert.append(neighbor)
        values = [columns, insert]

        sql = 'INSERT INTO subtask (%s) VALUES (%s) RETURNING subtask_id;'
        cur.execute(sql, values)
        subtask_id = cur.fetchone()
        subtask_id = subtask_id[0]
        sql = 'UPDATE subtask SET r_neighbor = %s ' \
              'Where part_of_teamboard=%s AND part_of_task=%s ' \
              'and part_of_column=%s and subtask_id= %s;'
        values = (subtask_id, data["teamboard"], data["task"], data["column"], neighbor)
        cur.execute(sql, values)
        print("Test: ID: ", subtask_id)
    return subtask_id


async def subtaskedit(data):
    teamboard_id = data["teamboard"]
    task_id = data["task"]
    column_id = data["column"]
    subtask_id = data["subtask"]
    max_columns = {"created", "deadline", "description", "color", "priority", "worker", "position", "name"}
    edit_columns = max_columns.intersection(data.keys())
    insert = [data[x] for x in edit_columns]

    edit_columns = tuple(edit_columns)

    # noinspection StrFormat
    sql = psycopg.sql.SQL('UPDATE subtask set {here} '
                           'WHERE teamboard_id = %s and task_id = %s and column_id = %s and subtask_id = %s;').format(
        here=psycopg.sql.SQL(', ').join(
            psycopg.sql.identifier(col) + psycopg.sql.SQL(' = %s') for col in edit_columns))

    with db.connect() as con:
        cur = con.cursor()
        cur.execute(sql, insert + [teamboard_id, task_id, column_id, subtask_id])
    return True


async def subtaskdelete(data):
    teamboard_id = data["teamboard"]
    task_id = data["task"]
    colum_id = data["column"]
    subtask_id = data["subtask"]
    sql = 'DELETE FROM subtask where ' \
          'subtask_id = %s and part_of_column = %s and part_of_task = %s and part_of_teamboard = %s;'
    with db.connect() as con:
        cur = con.cursor()
        cur.execute(sql, (colum_id, task_id, teamboard_id))


def subtaskmove(data):
    teamboard_id = data["teamboard"]
    task_id = data["task"]
    column_id = data["column"]
    subtask_id = data["subtask"]
    newposition = data["newPosition"]
    return positioncalc.move_subtask(teamboard_id, task_id, column_id, subtask_id, newposition)
