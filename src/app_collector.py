import requests
from datetime import datetime, timedelta
import logging
import time
import sqlite3
from .w_config import webhook_url, admin_id  # Да, pycharm ругается, но на VPS это работает.
import json

db_path = 'db.sqlite'  # БД лежит в той же папке
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO, filename='log/collector.log'
                    )
logger = logging.getLogger(__name__)


def check_tables():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    tables = cursor.execute('SELECT name from sqlite_master WHERE type = "table"').fetchall()  # Смотрим какие есть таблицы
    valid_tables = []
    for t in tables:
        valid_tables.append(t[0])
    if 'actual_data' not in valid_tables:  # Создание таблицы actual_data
        cursor.execute(
            'CREATE TABLE "actual_data" ( "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, "api_id" INTEGER NOT NULL, '
            '"name" TEXT, "name2" TEXT, "sell_price" REAL, "sell_offers" REAL, "buy_price" REAL, "buy_orders" REAL, '
            '"faction" TEXT, "rarity" TEXT, "margin" REAL, "crafting_margin" REAL, "category" TEXT, "_type" TEXT, '
            '"last_update_time" TEXT, "operation_time" TEXT )')
    elif 'all_collected_data' not in valid_tables:  # Создание таблицы all_collected_data
        cursor.execute(
            'CREATE TABLE "all_collected_data" ( "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, "api_id" INTEGER '
            'NOT NULL, "name" TEXT, "name2" TEXT, "sell_price" REAL, "sell_offers" REAL, "buy_price" REAL, '
            '"buy_orders" REAL, "faction" TEXT, "rarity" TEXT, "margin" REAL, "crafting_margin" REAL, "category" '
            'TEXT, "_type" TEXT, "last_update_time" TEXT, "operation_time" TEXT )')
    elif 'analyz_data' not in valid_tables:  # Создание таблицы analyz_data
        cursor.execute('CREATE TABLE analyz_data (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, datetime TEXT NOT '
                       'NULL, user_id TEXT NOT NULL, first_name TEXT, last_name TEXT, user_name TEXT NOT NULL, '
                       'button TEXT);')
        conn.commit()
    else:
        return


def do_alarm(t_alarmtext):
    headers = {"Content-type": "application/json"}
    payload = {"text": f"{t_alarmtext}", "chat_id": f"{admin_id}"}
    requests.post(url=webhook_url, data=json.dumps(payload), headers=headers)


def get_json_items(data=None):
    url = "https://crossoutdb.com/api/v1/items"
    r = requests.get(url, params=data)
    rsp = r.json()
    return rsp


def get_cursor_id(table_name):
    conn = sqlite3.connect(db_path)  # Инициируем подключение к БД
    cursor = conn.cursor()
    line_id = cursor.execute(f"select seq from sqlite_sequence where name='{table_name}'").fetchall()[0][0]
    conn.commit()
    return line_id


def data_recording():
    rsp = get_json_items({'language': 'ru'})
    conn = sqlite3.connect(db_path)  # Инициируем подключение к БД
    cursor = conn.cursor()
    first_id = get_cursor_id('all_collected_data')

    for r in rsp:
        api_id = r['id']
        name = r['localizedName']
        name_2 = r['availableName'].replace('\n', '').replace("'", '')
        sell_price = r['formatSellPrice']
        sell_offers = r['sellOffers']
        buy_price = r['formatBuyPrice']
        buy_orders = r['buyOrders']
        faction = str(r['faction']).replace('\n', '').replace("'", '')  # Убираем символы, которые не понравятся sqlite
        rarity = r['rarityName']
        margin = r['formatMargin']
        crafting_margin = r['formatCraftingMargin']
        category = r['categoryName']
        _type = r['typeName']
        last_update_time = r['lastUpdateTime']
        last_update_time_msk = datetime.strptime(last_update_time, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=180)
        operation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #        print('api_id: ', api_id, '| name:', name, '| name 2:', name_2, '| Sell Price:', sell_price,
        #              '| Sell Offers:', sell_offers, '|Buy Price: ', buy_price, '| Buy Orders: ', buy_orders,
        #              '| Faction:', faction, '| Rarity: ', rarity, '| Crafting Margin:', crafting_margin, '| Category:',
        #              category, '| Type:', _type, '| Last Update Time: ', last_update_time, '| Operation_time',
        #              operation_time)

        cursor.execute(
            f"INSERT INTO all_collected_data VALUES (Null, '{api_id}', '{name}', '{name_2}', '{sell_price}', '{sell_offers}', '{buy_price}', '{buy_orders}', '{faction}', '{rarity}', '{margin}', '{crafting_margin}', '{category}', '{_type}', '{last_update_time_msk}', '{operation_time}')")

        conn.commit()
    last_id = get_cursor_id('all_collected_data')
    cursor.execute("DELETE from actual_data")  # предварительно затираем то, что было в таблице res_h
    res = cursor.execute(
        f"SELECT * FROM all_collected_data WHERE id > {first_id} and id <= {last_id}").fetchall()
    conn.commit()
    # Записываем результаты последней проверки в таблицу res
    for r in res:
        r1 = r[1:16:1]  # Отсек первый элемент в каждом из списков (это id, чтоб не было конфликтов)
        cursor.execute(f"INSERT INTO actual_data VALUES (Null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", r1)
    conn.commit()
    logger.info('Data Recorded')


def remove_old_data():
    conn = sqlite3.connect(db_path)  # Инициируем подключение к БД
    cursor = conn.cursor()
    #  Рассчет актуального времени (текущая дата минус заданное количество минут (32 дня))
    actualtime = datetime.strftime((datetime.now() - timedelta(minutes=46080)), "%Y-%m-%d %H:%M:%S")
    cursor.execute(f"DELETE from all_collected_data WHERE operation_time < '{actualtime}'")
    conn.commit()


if __name__ == '__main__':
    try:
        while True:
            check_tables()
            data_recording()
            remove_old_data()
            time.sleep(240)
    except KeyboardInterrupt:
        print('Вы завершили работу программы collector')
        logger.info('Program has been stop manually')
    except Exception as e:
        t_alarmtext = f'Crossout_helper (app_collector.py): {str(e)}'
        do_alarm(t_alarmtext)
        logger.error(f'Other except error Exception', exc_info=True)
