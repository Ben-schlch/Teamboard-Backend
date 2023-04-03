import psycopg
from services.db import connect


async def column_current_position(teamboard, task_id, column_id):
    # Assume the task to be moved has a primary key value of 1 and its new position is 6
    # Get the current left and right neighbor IDs of the task
    with connect() as con:
        position = None
        cur = con.cursor()
        cur.execute("SELECT l_neighbor, r_neighbor FROM task_column "
                    "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s;",
                    [(teamboard,), (task_id,), (column_id,)])
        neighbors = cur.fetchone()
        l_neighbor = neighbors[0]
        position = 0
        if neighbors[0].isnumeric():
            position = 0
            while l_neighbor.isnumeric():
                position += 1
                cur.execute("SELECT l_neighbor FROM task_column "
                            "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s",
                            [(teamboard,), (task_id,), (l_neighbor,)])
                l_neighbor = cur.fetchone()
        return position, neighbors


async def column_adjust_old_neighbors(teamboard, task_id, neighbors):
    # Update the left neighbor's right_neighbor column if the task is not at the beginning
    with connect() as con:
        cur = con.cursor()
        if neighbors[0] is not None:
            cur.execute("UPDATE task_column SET r_neighbor = %s "
                        "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s",
                        (neighbors[1], teamboard, task_id, neighbors[0]))
        if neighbors[1] is not None:
            cur.execute("UPDATE task_column SET l_neighbor = %s "
                        "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s",
                        (neighbors[0], teamboard, task_id, neighbors[1]))


async def move_column(teamboard_id, task_id, column, new_position):
    # Move task to new position and update all involved neighbors
    old_position, neighbors = await column_current_position(teamboard_id, task_id, column)
    if new_position == old_position or new_position<0:
        return 0
    # Adjust the neighbors of the task to be moved
    await column_adjust_old_neighbors(teamboard_id, task_id, neighbors)
    if new_position < old_position:
        # iterate to find position left from itself
        new_position = old_position - new_position
        with connect() as con:
            left_neighbor = neighbors[0]
            for i in range(new_position):
                cur = con.cursor()
                left_neighbor = row[0]
                cur.execute("SELECT l_neighbor, column_id FROM task_column "
                            "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s",
                            [(teamboard_id,), (task_id,), (left_neighbor,)])
                row = cur.fetchone()
            new_right_neighbor = row[1]
            new_left_neighbor = row[0]
        cur.execute("UPDATE task_column SET r_neighbor = %s "
                    "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s;"
                    "UPDATE task_column SET l_neighbor = %s "
                    "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s;"
                    "UPDATE task_column SET r_neighbor = %s and l_neighbor = %s "
                    "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s;",
                    (column, teamboard_id, task_id, new_left_neighbor,
                     column, teamboard_id, task_id, new_right_neighbor,
                     new_right_neighbor, new_left_neighbor, teamboard_id, task_id, column))
    else:
        # iterate to find position right from itself
        new_position = new_position - old_position
        with connect() as con:
            right_neighbor = neighbors[1]
            for i in range(new_position):
                cur = con.cursor()
                cur.execute("SELECT r_neighbor, column_id FROM task_column "
                            "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s",
                            [(teamboard_id,), (task_id,), (right_neighbor,)])
                row = cur.fetchone()
                right_neighbor = row[0]
            new_right_neighbor = row[0]
            new_left_neighbor = row[1]

    cur.execute("UPDATE task_column SET r_neighbor = %s "
                "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s;"
                "UPDATE task_column SET l_neighbor = %s "
                "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s;"
                "UPDATE task_column SET r_neighbor = %s and l_neighbor = %s "
                "WHERE part_of_teamboard=%s and part_of_task=%s and column_id = %s;",
                (column, teamboard_id, task_id, new_left_neighbor,
                 column, teamboard_id, task_id, new_right_neighbor,
                 new_right_neighbor, new_left_neighbor, teamboard_id, task_id, column))