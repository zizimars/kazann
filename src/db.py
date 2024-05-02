import os
import datetime

import libsql_experimental as libsql


TABLE_NAME = "annotations"


url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

con = libsql.connect(
    "data/kazann.db",
    sync_url=url,
    auth_token=auth_token,
)
con.sync()


def init():
    try:
        # A table named 'annotations' with the following fields:
        # user_name: str, not null
        # id: int, not null
        # answer: int, not null
        # annotation: str, optional
        # the primary key is compound of user_id and id
        # con.execute('CREATE TABLE IF NOT EXISTS annotations (id INTEGER PRIMARY KEY, user_name TEXT NOT NULL, answer INTEGER NOT NULL, annotation TEXT, time DATETIME)')
        con.execute(
            f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} (id INTEGER PRIMARY KEY, user_name TEXT NOT NULL, answer INTEGER NOT NULL, annotation TEXT, time INTEGER)"
        )
    except:
        print("Table already exists")


def insert(
    user_name: str,
    id: int,
    answer: int,
    annotation: str,
    time: datetime.datetime,
):
    con.execute(
        f"INSERT INTO {TABLE_NAME} (user_name, id, answer, annotation, time) VALUES (?, ?, ?, ?, ?)",
        (
            user_name,
            id,
            answer,
            annotation,
            int(time.now(datetime.UTC).timestamp() * 1e3),
        ),
    )
    con.commit()


def update(
    user_name: str,
    id: int,
    answer: int,
    annotation: str | None,
    time: datetime.datetime,
):
    con.execute(
        f"UPDATE {TABLE_NAME} SET user_name = ?, answer = ?, annotation = ?, time = ? WHERE id = ?",
        (
            user_name,
            answer,
            annotation,
            int(time.now(datetime.UTC).timestamp() * 1e3),
            id,
        ),
    )
    con.commit()


def get_all_unique_ids():
    con.sync()
    return con.execute(f"SELECT DISTINCT id FROM {TABLE_NAME}").fetchall()


def to_csv():
    con.sync()
    with open("kazannotations.csv", "w") as f:
        for row in con.execute(f"SELECT * FROM {TABLE_NAME}"):
            f.write(",".join(str(x) for x in row) + "\n")
