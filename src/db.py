import sqlite3
import datetime


con = sqlite3.connect("data/kazannotations.db", check_same_thread=False)


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
            "CREATE TABLE IF NOT EXISTS kazannotations (id INTEGER PRIMARY KEY, user_name TEXT NOT NULL, answer INTEGER NOT NULL, annotation TEXT, time DATETIME)"
        )
    except sqlite3.IntegrityError:
        print("Table already exists")


def insert(
    user_name: str,
    id: int,
    answer: int,
    annotation: str | None,
    time: datetime.datetime,
):
    # time_str = time.strftime('%Y-%m-%d %H:%M:%S')
    con.execute(
        "INSERT INTO kazannotations (user_name, id, answer, annotation, time) VALUES (?, ?, ?, ?, ?)",
        (user_name, id, answer, annotation, time),
    )
    con.commit()


def update(
    user_name: str,
    id: int,
    answer: int,
    annotation: str | None,
    time: datetime.datetime,
):
    # time_str = time.strftime('%Y-%m-%d %H:%M:%S')
    con.execute(
        "UPDATE kazannotations SET user_name = ?, answer = ?, annotation = ?, time = ? WHERE id = ?",
        (user_name, answer, annotation, time, id),
    )
    con.commit()


def get_all_unique_ids():
    return con.execute("SELECT DISTINCT id FROM kazannotations").fetchall()


def to_csv():
    with open("kazannotations.csv", "w") as f:
        for row in con.execute("SELECT * FROM kazannotations"):
            f.write(",".join(str(x) for x in row) + "\n")
