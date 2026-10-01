import os
import time

import pymysql
from flask import Flask, jsonify

app = Flask(__name__)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "db"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "database": os.environ["DB_NAME"],
    "autocommit": True,
}


def get_connection(retries=10, delay=2):
    for attempt in range(retries):
        try:
            return pymysql.connect(**DB_CONFIG)
        except pymysql.err.OperationalError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)


def read_counter(cursor):
    cursor.execute("SELECT value FROM counter WHERE id = 1")
    return cursor.fetchone()[0]


@app.get("/api/health")
def health():
    return jsonify(status="ok")


@app.get("/api/counter")
def get_counter():
    with get_connection() as conn, conn.cursor() as cur:
        return jsonify(value=read_counter(cur))


@app.post("/api/counter")
def increment_counter():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("UPDATE counter SET value = value + 1 WHERE id = 1")
        return jsonify(value=read_counter(cur))
