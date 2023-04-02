import psycopg2
import os


def connect():
    """
    Connect to the teamboard database. Choice of Database might be enabled in the future
    :return: Connection to the database
    """
    conn = psycopg2.connect(host="localhost",
                            database="teamboard",
                            user="postgres",
                            password=os.getenv("pgsqlpw"))
    return conn


def insert_query(table: str, rows: list, values: list) -> int:
    """
    Function that executes an insert query on the teamboard database.
    :param table: The table that the query should be executed on
    :param rows: The rows that values should be inserted to
    :param values: The values that should be inserted into the rows.
    :param values: the number of values has to be the same as the number of rows
    :return: 0 if the query was successful, an error code if not
    """
    rows_sql = ", ".join(rows)
    values_sql = [f"'{val}'" if val else 'NULL' for val in values]
    values_sql = ", ".join(values_sql)
    sql = f"INSERT INTO %s (%s) VALUES(%s);"
    try:
        with connect() as con:
            cur = con.cursor()
            cur.execute(sql, (table, rows_sql, values_sql))
    except psycopg2.DatabaseError as err:
        return int(err.pgcode)
    return 0


def arbitrary_query(sql: str) -> int:
    """
    Function that executes an arbitrary query. Should be used, if the other functions are too limiting.
    :param sql: sql-query
    :return: 0 if successful, error code if not successful
    """
    sql_query = "%s;"
    try:
        with connect() as con:
            cur = con.cursor()
            cur.execute(sql, [sql_query])
    except psycopg2.Error as err:
        return int(err.pgcode)
    return 0


def select_query(table: str, columns: list[str], condition: str) -> int or list:
    """
    Function that executes a select query on the database.
    :param table: Table the query should be executed on
    :param columns: Values that should be returned
    :param condition: Arbitrary condition string
    :return: Error code or results if successful
    """

    columns_str = ", ".join(columns)
    sql = "SELECT %s FROM %s WHERE %s;"

    try:
        with connect() as con:
            cur = con.cursor()
            cur.execute(sql, [columns_str, table, condition])
            res = cur.fetchall()
            # creates a mapping of the selected columns to the values
            # There might be multiple vals per column -> iterate over all the results
            # response from db looks like this: list[(val1, val2,...), (val1, val2, ...), ...]
            # while the values are delivered in the same order they were queried
            res_mapped = [{f"{col}": f"{val}" for col, val in zip(columns, vals)} for vals in res]
            return res_mapped
    except psycopg2.Error as err:
        return int(err.pgcode)
