import psycopg2
import os


def connect():
    conn = psycopg2.connect(host="localhost", database="teamboard", user="postgres", password=os.getenv("pgsqlpw"))
    cur = conn.cursor()
    return conn, cur
