import psycopg
import os
from psycopg import sql as SQL
from psycopg.rows import dict_row, tuple_row


def connect(row_factory=tuple_row):
    """
    Connect to the teamboard database. Choice of Database might be enabled in the future
    :return: Connection to the database
    """
    conn = psycopg.connect(host="localhost",
                           dbname="teamboard",
                           user="postgres",
                           password=os.getenv("pgsqlpw"),
                           row_factory=row_factory)
    return conn


def insert_query(sql: str, params: tuple[any, ...]) -> int:
    """
    Function that executes an insert query on the teamboard database.
    :param sql: sql-query
    :param params: Parameters for the query
    """

    try:
        with connect() as con:
            cur = con.cursor()
            cur.execute(sql, params)
    except psycopg.DatabaseError as err:
        return int(err.sqlstate)
    return 0

#
# def arbitrary_query(sql: str) -> int:
#     """
#     Function that executes an arbitrary query. Should be used, if the other functions are too limiting.
#     :param sql: sql-query
#     :return: 0 if successful, error code if not successful
#     """
#     sql_query = "%s;"
#     try:
#         with connect() as con:
#             cur = con.cursor()
#             cur.execute(sql, [sql_query])
#     except psycopg.Error as err:
#         return int(err.pgcode)
#     return 0


def select_query(sql: str, params: tuple) -> int or list[dict[str, any]]:
    """
    Function that executes a select query on the database.
    :return: Error code or results if successful
    :return: Return is a list of dicts, where each dict represents a row and the keys are the column names
    """

    try:
        with connect(dict_row) as con:
            cur = con.cursor()
            cur.execute(sql, params)
            res = cur.fetchall()
            # creates a mapping of the selected columns to the values
            # There might be multiple vals per column -> iterate over all the results
            # response from db looks like this: list[(val1, val2,...), (val1, val2, ...), ...]
            # while the values are delivered in the same order they were queried
            # res_mapped = [{f"{col}": f"{val}" for col, val in zip(columns, vals)} for vals in res]
            return res
    except psycopg.Error as err:
        return int(err.sqlstate)
