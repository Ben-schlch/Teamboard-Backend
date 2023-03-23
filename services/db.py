import psycopg2
import os


def connect():
    conn = psycopg2.connect(host="localhost",
                            database="teamboard",
                            user="postgres",
                            password=os.getenv("pgsqlpw"))
    return conn


def insert_query(table, rows: list, values: list):
    rows_sql = ", ".join(rows)
    values_sql = [f"'{val}'" if val else 'NULL' for val in values]
    values_sql = ", ".join(values_sql)
    sql = f"INSERT INTO {table}({rows_sql}) VALUES({values_sql});"
    try:
        with connect() as con:
            cur = con.cursor()
            cur.execute(sql)
    except psycopg2.DatabaseError as err:
        return err.pgcode
    return False
