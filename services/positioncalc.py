from services.db import connect


async def column_current_position(teamboard, task_id, column_id):
    # Assume the task to be moved has a primary key value of 1 and its new position is 6
    # Get the current left and right neighbor IDs of the task
    with connect() as con:
        cur = con.cursor()
        sql = "SELECT l_neighbor, r_neighbor FROM task_column " \
              "WHERE part_of_teamboard=%s and part_of_task=%s and column_id=%s"
        cur.execute(query=sql, params=(teamboard, task_id, column_id))
        neighbors = list(cur.fetchone())
        position = 0
        if neighbors[0]:
            l_neighbor = neighbors[0]

            if isinstance(l_neighbor, int):

                while l_neighbor:
                    print("Left neighbor:", l_neighbor)
                    position += 1
                    sql = "SELECT l_neighbor FROM task_column " \
                          "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s"
                    cur.execute(sql, (teamboard, task_id, l_neighbor))
                    l_neighbor = cur.fetchone()[0]
        else:
            neighbors[0] = None
        if not neighbors[1]:
            neighbors[1] = None

        return position, neighbors


async def column_adjust_old_neighbors(teamboard, task_id, neighbors):
    # Update the left neighbor's right_neighbor column if the task is not at the beginning
    with connect() as con:
        cur = con.cursor()
        if neighbors[0] is not None:
            sql = "UPDATE task_column SET r_neighbor = %s " \
                  "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s"
            cur.execute(sql, (neighbors[1], teamboard, task_id, neighbors[0]))
        if neighbors[1] is not None:
            cur.execute("UPDATE task_column SET l_neighbor = %s "
                        "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s",
                        (neighbors[0], teamboard, task_id, neighbors[1]))


async def move_column(teamboard_id, task_id, column, new_position):
    # Move task to new position and update all involved neighbors
    old_position, neighbors = await column_current_position(teamboard_id, task_id, column)
    print("Oldposition:", old_position, " Neighbors:", neighbors, " Newposition:", new_position)
    if (new_position == old_position) or (new_position < 0):
        print("No move possible // already at position?!")
        return 0
    # Adjust the neighbors of the task to be moved
    await column_adjust_old_neighbors(teamboard_id, task_id, neighbors)
    row = None
    if new_position < old_position:
        # iterate to find position left from itself
        new_position = old_position - new_position
        with connect() as con:
            left_neighbor = neighbors[0]
            for i in range(new_position):
                print("Run:", i)
                cur = con.cursor()
                cur.execute("SELECT l_neighbor, column_id FROM task_column "
                            "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s",
                            (teamboard_id, task_id, left_neighbor))
                row = cur.fetchone()
                left_neighbor = row[0]

    else:
        # iterate to find position right from itself
        new_position = new_position - old_position
        with connect() as con:
            right_neighbor = neighbors[1]
            for i in range(new_position):
                cur = con.cursor()
                cur.execute("SELECT column_id, r_neighbor FROM task_column "
                            "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s",
                            (teamboard_id, task_id, right_neighbor))
                row = cur.fetchone()
    print(row)
    try:
        new_right_neighbor = row[1]
    except TypeError:
        new_right_neighbor = None
    try:
        new_left_neighbor = row[0]
    except TypeError:
        new_left_neighbor = None

    print("New right neighbor:", new_right_neighbor, " New left neighbor:", new_left_neighbor)
    with connect() as con:
        cur = con.cursor()
        cur.executemany("UPDATE task_column SET r_neighbor = %s "
                        "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s;",
                        ((column, teamboard_id, task_id, new_left_neighbor),
                         (new_right_neighbor, teamboard_id, task_id, column)))
        cur.executemany("UPDATE task_column SET l_neighbor = %s "
                        "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s;",
                        ((column, teamboard_id, task_id, new_right_neighbor),
                         (new_left_neighbor, teamboard_id, task_id, column)))
    return 1


async def subtask_current_position(teamboard_id, task_id, column_id, subtask_id):
    with connect() as con:
        cur = con.cursor()
        sql = "SELECT l_neighbor, r_neighbor FROM subtask " \
              "WHERE part_of_teamboard=%s and part_of_task=%s and part_of_column=%s and subtask_id=%s"
        cur.execute(query=sql, params=(teamboard_id, task_id, column_id, subtask_id))
        neighbors = list(cur.fetchone())
        position = 0
        if neighbors[0]:
            l_neighbor = neighbors[0]

            if isinstance(l_neighbor, int):

                while l_neighbor:
                    print("Left neighbor:", l_neighbor)
                    position += 1
                    sql = "SELECT l_neighbor FROM subtask " \
                          "WHERE part_of_teamboard=%s and part_of_task=%s and part_of_column = %s and subtask_id = %s"
                    cur.execute(sql, (teamboard_id, task_id, column_id, l_neighbor))
                    l_neighbor = cur.fetchone()[0]
        else:
            neighbors[0] = None
        if not neighbors[1]:
            neighbors[1] = None

        return position, neighbors


async def subtask_adjust_old_neighbors(teamboard_id, task_id, column_id, neighbors):
    with connect() as con:
        cur = con.cursor()
        if neighbors[0] is not None:
            sql = "UPDATE subtask SET r_neighbor = %s " \
                  "WHERE part_of_teamboard=%s and part_of_task=%s and part_of_column = %s and subtask_id = %s"
            cur.execute(sql, (neighbors[1], teamboard_id, task_id, column_id, neighbors[0]))
        if neighbors[1] is not None:
            cur.execute("UPDATE subtask SET l_neighbor = %s "
                        "WHERE part_of_teamboard=%s and part_of_task=%s and part_of_column = %s and subtask_id = %s",
                        (neighbors[0], teamboard_id, task_id, column_id, neighbors[1]))


async def move_subtask(teamboard_id, task_id, column_id, subtask_id, new_position):
    # Move task to new position and update all involved neighbors
    old_position, neighbors = await subtask_current_position(teamboard_id, task_id, column_id, subtask_id)
    print("Oldposition:", old_position, " Neighbors:", neighbors, " Newposition:", new_position)
    if (new_position == old_position) or (new_position < 0):
        print("No move possible // already at position?!")
        return 0
    # Adjust the neighbors of the task to be moved
    await subtask_adjust_old_neighbors(teamboard_id, task_id, column_id, neighbors)

    row = None
    if new_position < old_position:
        # iterate to find position left from itself
        new_position = old_position - new_position
        with connect() as con:
            left_neighbor = neighbors[0]
            for i in range(new_position):
                print("Run:", i)
                cur = con.cursor()
                cur.execute("SELECT l_neighbor, subtask_id FROM subtask WHERE "
                            "part_of_teamboard=%s and part_of_task=%s and part_of_column = %s and subtask_id = %s",
                            (teamboard_id, task_id, column_id, left_neighbor))
                row = cur.fetchone()
                left_neighbor = row[0]

    else:
        # iterate to find position right from itself
        new_position = new_position - old_position
        with connect() as con:
            right_neighbor = neighbors[1]
            for i in range(new_position):
                cur = con.cursor()
                cur.execute("SELECT subtask_id, r_neighbor FROM subtask WHERE "
                            "part_of_teamboard=%s and part_of_task=%s and part_of_column = %s and subtask_id = %s",
                            (teamboard_id, task_id, right_neighbor))
                row = cur.fetchone()
    print(row)
    try:
        new_right_neighbor = row[1]
    except TypeError:
        new_right_neighbor = None
    try:
        new_left_neighbor = row[0]
    except TypeError:
        new_left_neighbor = None

    print("New right neighbor:", new_right_neighbor, " New left neighbor:", new_left_neighbor)
    with connect() as con:
        cur = con.cursor()
        cur.executemany("UPDATE subtask SET r_neighbor = %s "
                        "WHERE part_of_teamboard=%s and part_of_task=%s and part_of_column = %s and subtask_id=%s;",
                        ((subtask_id, teamboard_id, task_id, column_id, new_left_neighbor),
                         (new_right_neighbor, teamboard_id, task_id, column_id, subtask_id)))
        cur.executemany("UPDATE subtask SET l_neighbor = %s "
                        "WHERE part_of_teamboard=%s and part_of_task=%s and part_of_column = %s and subtask_id=%s;",
                        ((subtask_id, teamboard_id, task_id, column_id, new_right_neighbor),
                         (new_left_neighbor, teamboard_id, task_id, column_id, subtask_id)))
    return 1


async def move_between_states(teamboard_id, task_id, column_id, subtask_id, new_position):
    # get the old column id and check if subtask exists in teamboard
    old_column_id = None
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT part_of_column FROM subtask WHERE "
                    "part_of_teamboard=%s AND part_of_task=%s AND subtask_id=%s", (teamboard_id, task_id, subtask_id,))
        old_column_id = cur.fetchone()[0]
    if old_column_id is None:
        return 0
    # get the old position and the neighbors of the subtask
    old_position, neighbors = await subtask_current_position(teamboard_id, task_id, old_column_id, subtask_id)
    await subtask_adjust_old_neighbors(teamboard_id, task_id, old_column_id, neighbors)
    with connect() as con:
        # get the first subtask of the list
        cur = con.cursor()
        cur.execute("SELECT l_neighbor, r_neighbor FROM subtask WHERE "
                    "part_of_teamboard = %s AND part_of_task = %s AND part_of_column = %s AND l_neighbor is NULL",
                    (teamboard_id, task_id, column_id,))
        row = cur.fetchone()
        left_neighbor, right_neighbor = row if row else (None, None)
        if not row:
            new_position = 0
        # iterate until finding the position
        for i in range(new_position):
            cur.execute("SELECT subtask_id, r_neighbor FROM subtask WHERE "
                        "part_of_teamboard = %s AND part_of_task = %s AND part_of_column = %s AND subtask_id = %s",
                        (teamboard_id, task_id, column_id, right_neighbor))
            row = cur.fetchone()
            left_neighbor, right_neighbor = row if row else (None, None)
            if i < new_position - 1 and right_neighbor is None:
                return 0

        cur.execute("UPDATE subtask SET l_neighbor = %s, r_neighbor = %s, part_of_column = %s "
                    "WHERE part_of_teamboard=%s and part_of_task=%s and part_of_column = %s and subtask_id=%s;",
                    (left_neighbor, right_neighbor, column_id, teamboard_id, task_id, old_column_id, subtask_id))
        # update the neighbors of the subtask
        if left_neighbor:
            cur.execute("UPDATE subtask SET r_neighbor = %s "
                        "WHERE part_of_teamboard=%s and part_of_task=%s and part_of_column = %s and subtask_id=%s;",
                        (subtask_id, teamboard_id, task_id, column_id, left_neighbor))
        if right_neighbor:
            cur.execute("UPDATE subtask SET l_neighbor = %s "
                        "WHERE part_of_teamboard=%s and part_of_task=%s and part_of_column = %s and subtask_id=%s;",
                        (subtask_id, teamboard_id, task_id, column_id, right_neighbor))
    return 1
