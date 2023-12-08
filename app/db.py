import os
import sys
import psycopg2


CONN = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    database=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)
CURS = DB = None


def connect():
    global CURS, DB
    try:
        CURS = CONN.cursor()
        DB = CURS.execute
    except psycopg2.DatabaseError as e:
        if CONN:
            CONN.rollback()
        print(e)
        sys.exit


def get_db():
    if not (CONN and CURS and DB):
        connect()
    return (CONN, CURS, DB)


connect()
get_db()
