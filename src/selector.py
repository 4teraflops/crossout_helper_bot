import sqlite3
import os


db_path = os.getcwd() + os.sep + 'src' + os.sep + 'db.sqlite'


def _get_top5_crafting(rare):
    conn = sqlite3.connect(db_path)  # Инициируем подключение к БД
    cursor = conn.cursor()

    if rare == 'All':
        res = cursor.execute(
            f'SELECT name, crafting_margin FROM actual_data ORDER by crafting_margin DESC LIMIT 5').fetchall()
        text = f'НАЗВАНИЕ: ПРОФИТ\n\n{res[0][0]}: {res[0][1]}\n{res[1][0]}: {res[1][1]}\n{res[2][0]}: {res[2][1]}\n{res[3][0]}: {res[3][1]}\n{res[4][0]}: {res[4][1]}'
        return text
    else:
        res = cursor.execute(f'SELECT name, crafting_margin FROM actual_data WHERE rarity = "{rare}" ORDER by crafting_margin DESC LIMIT 5').fetchall()
        text = f'НАЗВАНИЕ: ПРОФИТ\n\n{res[0][0]}: {res[0][1]}\n{res[1][0]}: {res[1][1]}\n{res[2][0]}: {res[2][1]}\n{res[3][0]}: {res[3][1]}\n{res[4][0]}: {res[4][1]}'
        return text


def _get_top5_reselling():
    conn = sqlite3.connect(db_path)  # Инициируем подключение к БД
    cursor = conn.cursor()

    res = cursor.execute('SELECT name, margin FROM actual_data ORDER by margin DESC LIMIT 5').fetchall()
    text = f'Название | Профит\n\n{res[0][0]} | {res[0][1]}\n' \
           f'{res[1][0]} | {res[1][1]}\n' \
           f'{res[2][0]} | {res[2][1]}\n' \
           f'{res[3][0]} | {res[3][1]}\n' \
           f'{res[4][0]} | {res[4][1]}\n'
    return text


def get_top_10_difference_prices(time):
    conn = sqlite3.connect(db_path)  # Инициируем подключение к БД
    cursor = conn.cursor()

    res = cursor.execute(f"SELECT name2, {time}_sign, diff_sell_price_{time} FROM difference_sell_price ORDER BY -diff_sell_price_{time} LIMIT 10").fetchall()

    text = f'Название | скачек цены\n\n' \
           f'{res[0][0]} {res[0][1]} {res[0][2]}\n' \
           f'{res[1][0]} {res[1][1]} {res[1][2]}\n' \
           f'{res[2][0]} {res[2][1]} {res[2][2]}\n' \
           f'{res[3][0]} {res[3][1]} {res[3][2]}\n' \
           f'{res[4][0]} {res[4][1]} {res[4][2]}\n' \
           f'{res[5][0]} {res[5][1]} {res[5][2]}\n' \
           f'{res[6][0]} {res[6][1]} {res[6][2]}\n' \
           f'{res[7][0]} {res[7][1]} {res[7][2]}\n' \
           f'{res[8][0]} {res[8][1]} {res[8][2]}\n' \
           f'{res[9][0]} {res[9][1]} {res[9][2]}\n'
    return text