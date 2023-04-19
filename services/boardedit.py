import json
import psycopg
import services.db as db
import services.positioncalc as positioncalc
import logging


async def teamboardload(email):
    sql_teamboard = 'SELECT teamboard_name, teamboard_id FROM teamboard ' \
          'WHERE teamboard_id IN (' \
          'SELECT teamboard FROM teamboard_editors ' \
          'WHERE editor = %s);'

    values = (email,)
    teamboards = db.select_query(sql_teamboard, values)
    for t in teamboards:
        t["tasks"] = await tasklist_helper(t["teamboard_id"])
    return json.dumps(teamboards)


async def tasklist_helper(teamboard_id: int) -> list:
    sql_task = "SELECT task_name, task_id FROM task " \
                     "WHERE part_of_teamboard = %s"
    values = (teamboard_id,)
    tasks = db.select_query(sql_task, values)
    for task in tasks:
        task["states"] = await statelist_helper(task["task_id"])
        task["name"] = task.pop("task_name")
    return tasks


async def statelist_helper(task_id: int) -> list:
    sql_first_state = "SELECT name_of_column, column_id, r_neighbor FROM task_column " \
                      "WHERE part_of_task = %s " \
                      "AND l_neighbor is NULL;"
    sql_state = "SELECT name_of_column, column_id, r_neighbor FROM task_column " \
                "WHERE column_id = %s;"
    states = []
    values = (task_id,)
    state = db.select_query(sql_first_state, values)
    if not state:
        return []
    states.append({"name": state[0]["name_of_column"], "subtasks": await subtasklist_helper(state[0]["column_id"])})
    r_neighbor = state[0]["r_neighbor"]
    while r_neighbor:
        values = (r_neighbor, )
        state = db.select_query(sql_state, values)
        if not state:
            return states
        states.append({"name": state[0]["name_of_column"],
                       "subtasks": await subtasklist_helper(state[0]["column_id"])})
        r_neighbor = state[0]["r_neighbor"]
    return states


async def subtasklist_helper(state_id: int) -> list:
    sql_first_subtask = "SELECT subtask_name, subtask_id, r_neighbor, description, worker FROM subtask " \
                        "WHERE part_of_column = %s " \
                        "AND l_neighbor is NULL;"
    sql_subtask = "SELECT subtask_name, subtask_id, r_neighbor, description, worker FROM subtask " \
                  "WHERE subtask_id = %s;"
    subtasks = []
    values = (state_id, )
    subtask = db.select_query(sql_first_subtask, values)
    if not subtask:
        return []
    subtasks.append({"name": subtask[0]["subtask_name"],
                     "description": subtask[0]["description"],
                     "worker": subtask[0]["worker"]})
    r_neighbor = subtask[0]["r_neighbor"]
    while r_neighbor:
        values = (r_neighbor, )
        subtask = db.select_query(sql_subtask, values)
        if not subtask:
            return subtasks
        subtasks.append({"name": subtask[0]["subtask_name"],
                         "description": subtask[0]["description"],
                         "worker": subtask[0]["worker"]})
        r_neighbor = subtask[0]["r_neighbor"]
    return subtasks


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
    sql = 'INSERT INTO teamboard (teamboard_name) VALUES (%s) returning teamboard_id;'
    values = (data["teamboard"]["name"],)
    with db.connect() as con:
        cur = con.cursor()
        cur.execute(sql, values)
        teamboard_id = cur.fetchone()[0]
        sql = 'INSERT INTO teamboard_editors (teamboard, editor) VALUES (%s, %s);'
        cur.execute(sql, (teamboard_id, email))
    data["teamboard"]["id"] = teamboard_id
    return data


async def teamboarddelete(data, manager):
    sql = 'SELECT Count(1) from teamboard where teamboard_id = %s;'
    with db.connect() as con:
        cur = con.cursor()
        teamboard = data["teamboard"]["id"]
        cur.execute(sql, (teamboard,))
        exists = cur.fetchone()[0]
        exists = exists > 0
        if exists:
            sql = "SELECT editor FROM teamboard_editors WHERE teamboard = %s"
            cur.execute(sql, (teamboard,))
            editors = cur.fetchall()
            editors = [item[0] for item in editors]
            sql = 'DELETE FROM teamboard where teamboard_id = %s;'
            cur.execute(sql, (teamboard,))
            for connection in [item[0] for item in manager.active_connections if item[1] in editors]:
                await connection.send_text(json.dumps(data))
            return data
        else:
            raise psycopg.Error


async def teamboardedit(data):
    teamboard_id = data["teamboard"]["id"]
    sql = 'UPDATE teamboard set teamboard_name = %s WHERE teamboard_id = %s;'
    values = (data["teamboard"]["name"], teamboard_id)
    with db.connect() as con:
        cur = con.cursor()
        cur.execute(sql, values)
    return data


async def taskcreate(data):
    teamboard_id = data["teamboard_id"]
    task_name = data["task"]["name"]
    logging.info(f"taskcreate: {teamboard_id}, {task_name}")
    sql = 'INSERT INTO task (part_of_teamboard, task_name) VALUES (%s, %s) RETURNING task_id;'
    values = (teamboard_id, task_name,)
    with db.connect() as con:
        cur = con.cursor()
        cur.execute(sql, values)
        task_id = cur.fetchone()[0]
    data["task"]["id"] = task_id
    logging.info(f"taskcreate: successfull with new id: {task_id}")
    return data


async def taskdelete(data):
    teamboard_id = data["teamboard_id"]
    task_id = data["task"]["id"]
    sql = 'DELETE FROM task where  task_id = %s and part_of_teamboard = %s;'
    with db.connect() as con:
        cur = con.cursor()
        cur.execute(sql, (task_id, teamboard_id))

    return data


async def taskedit(data):
    teamboard_id = data["teamboard_id"]
    task_id = data["task"]["id"]
    task_name = data["task"]["name"]
    sql = 'UPDATE task set task_name = %s WHERE part_of_teamboard = %s and task_id = %s;'
    values = [task_name, teamboard_id, task_id]
    with db.connect() as con:
        cur = con.cursor()
        cur.execute(sql, values)
    return data


async def columndelete(data: dict):
    teamboard_id = data["teamboard_id"]
    task_id = data["task_id"]
    column_id = data["state"]["id"]

    with db.connect() as con:
        cur = con.cursor()
        sql = "SELECT l_neighbor, r_neighbor FROM task_column " \
              "WHERE part_of_teamboard=%s and part_of_task=%s and column_id=%s"
        cur.execute(query=sql, params=(teamboard_id, task_id, column_id))
        neighbors = list(cur.fetchone())
        await positioncalc.column_adjust_old_neighbors(teamboard_id, task_id, neighbors)

        sql = 'DELETE FROM task_column where  column_id = %s and part_of_task = %s and part_of_teamboard = %s;'
        cur.execute(sql, (column_id, task_id, teamboard_id))
    return data


async def columncreate(data):
    teamboard_id = data["teamboard_id"]
    task_id = data["task_id"]
    column_name = data["state"]["state"]
    sql = 'SELECT column_id FROM task_column WHERE part_of_teamboard=%s AND part_of_task=%s and r_neighbor IS NULL;'
    values = (teamboard_id, task_id)
    with db.connect() as con:
        cur = con.cursor()
        cur.execute(sql, values)
        column_id = cur.fetchone()
        if column_id is None:
            column_id = None
        else:
            column_id = column_id[0]
        sql = 'INSERT INTO task_column (part_of_teamboard, part_of_task, name_of_column, l_neighbor) ' \
              'VALUES (%s, %s, %s, %s) RETURNING column_id;'
        values = (teamboard_id, task_id, column_name, column_id)
        cur.execute(sql, values)
        new_column_id = cur.fetchone()[0]

        if column_id:
            sql = 'UPDATE task_column SET r_neighbor = %s ' \
                  'Where part_of_teamboard=%s AND part_of_task=%s and column_id= %s and r_neighbor IS NULL;'
            values = (new_column_id, teamboard_id, task_id, column_id)
            cur.execute(sql, values)
    print("Test: ID: ", new_column_id)
    data["state"]["id"] = new_column_id
    return new_column_id


async def columnmove(data):
    teamboard_id = data["teamboard_id"]
    task_id = data["task_id"]
    colum_id = data["state"]["id"]
    newposition = data["newPosition"]
    await positioncalc.move_column(teamboard_id, task_id, colum_id, newposition)
    return data


async def columnedit(data):
    teamboard_id = data["teamboard_id"]
    task_id = data["task_id"]
    column_id = data["state"]["id"]
    name = data["state"]["state"]
    sql = 'UPDATE task_column set name_of_column = %s ' \
          'WHERE part_of_teamboard = %s and part_of_task = %s and column_id = %s;'
    values = [name, teamboard_id, task_id, column_id]
    with db.connect() as con:
        cur = con.cursor()
        cur.execute(sql, values)
    return data


async def subtaskcreate(data):
    max_columns = {
        "deadline": "",
        "description": "",
        "color": "",
        "priority": "",
        "worker": "",
        "position": ""
    }
    max_columns.update(data["subtask"])
    with db.connect() as con:
        cur = con.cursor()
        sql = 'SELECT subtask_id FROM subtask WHERE part_of_teamboard=%s ' \
              'AND part_of_task=%s and part_of_column=%s and r_neighbor IS NULL;'
        values = (data["teamboard_id"], data["task_id"], data["state_id"])
        cur.execute(sql, values)
        l_neighbor = cur.fetchone()
        if l_neighbor is None:
            l_neighbor = None
        else:
            l_neighbor = l_neighbor[0]

        if not max_columns["worker"]:
            max_columns = None

        if max_columns["deadline"] == "":
            max_columns["deadline"] = None

        sql = "INSERT INTO subtask " \
              "(part_of_teamboard, part_of_task, part_of_column, " \
              "subtask_name, deadline, color, description, worker, l_neighbor) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s ) RETURNING subtask_id;"
        values = (data["teamboard_id"], data["task_id"], data["state_id"], max_columns["name"],
                  max_columns["deadline"],
                  max_columns["color"], max_columns["description"], max_columns["worker"], l_neighbor)
        cur.execute(sql, values)
        subtask_id = cur.fetchone()[0]
        if l_neighbor:

            sql = 'UPDATE subtask SET r_neighbor = %s ' \
                  'Where part_of_teamboard=%s AND part_of_task=%s ' \
                  'and part_of_column=%s and subtask_id= %s;'
            values = (subtask_id, data["teamboard_id"], data["task_id"], data["state_id"], l_neighbor)
            cur.execute(sql, values)
        print("Test: ID: ", subtask_id)
        data["subtask"]["id"] = subtask_id
    return data


async def subtaskedit(data):
    max_columns = {
        "name": "",
        "created": "",
        "deadline": "",
        "description": "",
        "color": "",
        "priority": "",
        "worker": "",
        "position": ""
    }
    max_columns.update(data["subtask"])
    if not max_columns["worker"]:
        max_columns["worker"] = None

    with db.connect() as con:
        cur = con.cursor()
        sql = "UPDATE subtask " \
              "SET subtask_name = %s, created = %s, deadline = %s, color = %s, description = %s, worker = %s " \
              "WHERE part_of_teamboard = %s and part_of_task = %s and part_of_column = %s and subtask_id = %s;"
        values = (max_columns["name"], max_columns["created"], max_columns["deadline"], max_columns["color"],
                  max_columns["description"], max_columns["worker"], data["teamboard_id"], data["task_id"], data["state_id"],
                  data["subtask"]["id"])
        cur.execute(sql, values)
    return data


async def subtaskdelete(data):
    teamboard_id = data["teamboard_id"]
    task_id = data["task_id"]
    column_id = data["state_id"]
    subtask_id = data["subtask"]["id"]
    with db.connect() as con:
        cur = con.cursor()
        sql = "SELECT l_neighbor, r_neighbor FROM subtask " \
              "WHERE part_of_teamboard=%s and part_of_task=%s and part_of_column=%s and subtask_id=%s"
        cur.execute(query=sql, params=(teamboard_id, task_id, column_id, subtask_id))
        neighbors = list(cur.fetchone())
        await positioncalc.subtask_adjust_old_neighbors(teamboard_id, task_id, column_id, neighbors)

        sql = 'DELETE FROM subtask ' \
              'where part_of_column = %s and part_of_task = %s and part_of_teamboard = %s and subtask_id = %s;'
        cur.execute(sql, (column_id, task_id, teamboard_id, subtask_id))
    return data


async def subtaskmove(data):
    teamboard_id = data["teamboard_id"]
    task_id = data["task_id"]
    column_id = data["state_id"]
    subtask_id = data["subtask"]["id"]
    newposition = data["newPosition"]
    await positioncalc.move_subtask(teamboard_id, task_id, column_id, subtask_id, newposition)
    return data
