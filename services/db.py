import psycopg
import os


def connect():
    """
    Connect to the teamboard database. Choice of Database might be enabled in the future
    :return: Connection to the database
    """
    conn = psycopg.connect(host="localhost",
                           dbname="teamboard",
                           user="postgres",
                           password=os.getenv("pgsqlpw"))
    return conn


# def insert_query(sql: str, params: tuple[any, ...]) -> int:
#     """
#     Function that executes an insert query on the teamboard database.
#     :param sql: sql-query
#     :param params: Parameters for the query
#     """
#
#     try:
#         with connect() as con:
#             cur = con.cursor()
#             cur.execute(sql, params)
#     except psycopg.DatabaseError as err:
#         return int(err.args[0])
#     return 0

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
#
#
# def select_query(table: str, columns: list[str], condition: str) -> int or list:
#     """
#     Function that executes a select query on the database.
#     :param table: Table the query should be executed on
#     :param columns: Values that should be returned
#     :param condition: Arbitrary condition string
#     :return: Error code or results if successful
#     """
#
#     columns_str = ", ".join(columns)
#     sql = "SELECT %s FROM %s WHERE %s;"
#
#     try:
#         with connect() as con:
#             cur = con.cursor()
#             cur.execute(sql, [columns_str, table, condition])
#             res = cur.fetchall()
#             # creates a mapping of the selected columns to the values
#             # There might be multiple vals per column -> iterate over all the results
#             # response from db looks like this: list[(val1, val2,...), (val1, val2, ...), ...]
#             # while the values are delivered in the same order they were queried
#             res_mapped = [{f"{col}": f"{val}" for col, val in zip(columns, vals)} for vals in res]
#             return res_mapped
#     except psycopg.Error as err:
#         return int(err.pgcode)
