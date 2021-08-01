import psycopg2
from flask import g


def connect_db():
    conn = psycopg2.connect(database="map", user="meng", password="123456", host="127.0.0.1", port="5432")
    return conn


def get_db():
    if not hasattr(g, 'pg_conn'):
        g.pg_conn = connect_db()
    return g.pg_conn


def disconnect_db(conn):
    conn.close()


def select_table(sql):
    conn = get_db()

    cur = conn.cursor()

    cur.execute(sql)
    rows = cur.fetchall()

    return rows


def insert_table(table, row):
    conn = get_db()
    ret = True

    columns = []
    values = []
    for key, value in row.items():
        columns.append(key)
        values.append(value)

    try:
        cur = conn.cursor()
        sql = "insert into %s (%s) values(%s)" % (table, ",".join(columns), ",".join(values))
        cur.execute(sql)
        conn.commit()
    except psycopg2.errors.UniqueViolation as e:
        ret = False

    return ret


