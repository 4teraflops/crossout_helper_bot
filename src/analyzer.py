import sqlite3
from datetime import datetime


db_path = 'src/db.sqlite'  # БД лежит в той же папке, но путь указывается относительно файла crafting_margin, т.к. функция исполняеется из него


def insert_in_analyz_table(user_id, first_name, last_name, user_name, button):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    actualtime = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    cursor.execute(f'INSERT INTO analyz_data VALUES (Null, "{actualtime}", "{user_id}", "{first_name}", "{last_name}", "{user_name}", "{button}")')
    conn.commit()
