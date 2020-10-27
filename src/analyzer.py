import sqlite3
from datetime import datetime
import os
import requests
from src.config import webhook_url, admin_id
import json

# БД лежит в той же папке, но путь указывается относительно файла crafting_margin, т.к. функция исполняеется из него
db_path = '/home/pirat/soft/collector_crossoutdb/src/db.sqlite'


def insert_in_analyz_table(user_id, first_name, last_name, user_name, button):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    actualtime = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    cursor.execute(f'INSERT INTO analyz_data VALUES (Null, "{actualtime}", "{user_id}", "{first_name}", "{last_name}", "{user_name}", "{button}")')
    conn.commit()


def do_alarm(t_alarmtext):
    headers = {"Content-type": "application/json"}
    payload = {"text": f"{t_alarmtext}", "chat_id": f"{admin_id}"}
    requests.post(url=webhook_url, data=json.dumps(payload), headers=headers)