import requests
from datetime import datetime, timedelta
import logging
import time
import sqlite3
from .w_config import webhook_url, admin_id  # Да, pycharm ругается, но это работает.
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
        conn.commit()
    elif 'all_collected_data' not in valid_tables:  # Создание таблицы all_collected_data
        cursor.execute(
            'CREATE TABLE "all_collected_data" ( "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, "api_id" INTEGER '
            'NOT NULL, "name" TEXT, "name2" TEXT, "sell_price" REAL, "sell_offers" REAL, "buy_price" REAL, '
            '"buy_orders" REAL, "faction" TEXT, "rarity" TEXT, "margin" REAL, "crafting_margin" REAL, "category" '
            'TEXT, "_type" TEXT, "last_update_time" TEXT, "operation_time" TEXT )')
        conn.commit()
    elif 'analyz_data' not in valid_tables:  # Создание таблицы analyz_data
        cursor.execute('CREATE TABLE "analyz_data" (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, datetime TEXT NOT '
                       'NULL, user_id TEXT NOT NULL, first_name TEXT, last_name TEXT, user_name TEXT NOT NULL, '
                       'button TEXT)')
    elif 'difference_sell_price' not in valid_tables:
        cursor.execute('CREATE TABLE "difference_sell_price" ("id" INTEGER NOT NULL, "api_id" REAL NOT NULL, '
                       '"name2" TEXT NOT NULL, "rarity" TEXT NOT NULL, "actual_price" REAL NOT NULL, "one_day_sign" '
                       'TEXT NOT NULL, "diff_sell_price_one_day" REAL NOT NULL, "three_days_sign" TEXT NOT NULL, '
                       '"diff_sell_price_three_days" REAL NOT NULL, "week_sign" TEXT NOT NULL, "diff_sell_price_week" '
                       'REAL NOT NULL, "month_sign" TEXT NOT NULL, "diff_sell_price_month" REAL NOT NULL, '
                       'PRIMARY KEY("id" AUTOINCREMENT))')
        conn.commit()
    else:
        return


def do_alarm(t_alarmtext):
    headers = {"Content-type": "application/json"}
    payload = {"text": f"{t_alarmtext}", "chat_id": f"{admin_id}"}
    requests.post(url=webhook_url, data=json.dumps(payload), headers=headers)


def get_json_items(params):
    url = "https://crossoutdb.com/api/v1/items"
    r = requests.get(url, params=params)
    rsp = r.json()
    return rsp


def get_cursor_id(table_name):
    conn = sqlite3.connect(db_path)  # Инициируем подключение к БД
    cursor = conn.cursor()
    line_id = cursor.execute(f"select seq from sqlite_sequence where name='{table_name}'").fetchall()[0][0]
    conn.commit()
    return line_id


def api_data_recording():
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


def remove_old_data_from_all_collected_data():
    conn = sqlite3.connect(db_path)  # Инициируем подключение к БД
    cursor = conn.cursor()
    #  Рассчет актуального времени (текущая дата минус заданное количество минут (32 дня))
    actualtime = datetime.strftime((datetime.now() - timedelta(minutes=46080)), "%Y-%m-%d %H:%M:%S")
    cursor.execute(f"DELETE from all_collected_data WHERE operation_time < '{actualtime}'")
    conn.commit()


def get_sell_price_from_historycal_data(api_id, start_time, end_time):
    conn = sqlite3.connect(db_path)  # Инициируем подключение к БД
    cursor = conn.cursor()
    price = cursor.execute(
        f"SELECT sell_price from all_collected_data WHERE operation_time >= '{start_time}' AND operation_time <= '{end_time}' AND api_id = '{api_id}' LIMIT 1").fetchall()
    # если данные не найдены, то присваиваем значение 'None'
    try:
        price = price[0][0]
    except IndexError:
        price = 0
        conn.commit()
    conn.commit()
    # если загрузилось пустое множество, то тоже присваиваем none
    if price:
        conn.commit()
        return price
    else:
        return 0


def assign_sign_to_sell_price(diff):
    sign = 0
    if diff > 0:
        sign = '🔺'
    elif diff < 0:
        sign = '🔻'
    elif diff == 0:
        sign = 0

    return sign


def collect_diff_data_to_bd():
    conn = sqlite3.connect(db_path)  # Инициируем подключение к БД
    cursor = conn.cursor()
    cursor.execute("DELETE from difference_sell_price")  # предварительно затираем то, что было в таблице difference_sell_price
    one_day_ago_time = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    one_day_ago_time_allowence = (datetime.now() - timedelta(days=1) + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")

    three_days_ago_time = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
    three_days_ago_time_allowence = (datetime.now() - timedelta(days=3) + timedelta(minutes=30)).strftime(
        "%Y-%m-%d %H:%M:%S")

    week_ago_time = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    week_ago_time_allowence = (datetime.now() - timedelta(days=7) + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")

    month_ago_time = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    month_ago_time_allowence = (datetime.now() - timedelta(days=30) + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")

    api_ids = cursor.execute("SELECT api_id from actual_data").fetchall()
    conn.commit()

    for api_id in api_ids:
        api_id = api_id[0]
        # Получил данные из таблицы
        name2 = cursor.execute(f'SELECT name2 FROM actual_data WHERE api_id = "{api_id}"').fetchall()[0][0]
        rarity = cursor.execute(f'SELECT rarity FROM actual_data WHERE api_id = "{api_id}"').fetchall()[0][0]
        actual_sell_price = cursor.execute(f'SELECT sell_price FROM actual_data WHERE api_id = "{api_id}"').fetchall()[0][0]

        sell_price_one_day_ago = get_sell_price_from_historycal_data(api_id, one_day_ago_time, one_day_ago_time_allowence)
        sell_price_three_days_ago = get_sell_price_from_historycal_data(api_id, three_days_ago_time,
                                                                        three_days_ago_time_allowence)
        sell_price_week_ago = get_sell_price_from_historycal_data(api_id, week_ago_time, week_ago_time_allowence)
        sell_price_month_ago = get_sell_price_from_historycal_data(api_id, month_ago_time, month_ago_time_allowence)
        # Посчитал разницу (на случай, если одна из цен вернулась 0, значит данных нет и считать разницу не надо)
        # Так же признак + или - пишем отдельным значением
        if sell_price_one_day_ago == 0:
            diff_sell_price_one_day = 0
            one_day_sign = 0
        else:
            diff_sell_price_one_day = round((actual_sell_price - sell_price_one_day_ago), 2)
            one_day_sign = assign_sign_to_sell_price(diff_sell_price_one_day)

        if sell_price_three_days_ago == 0:
            diff_sell_price_three_days = 0
            three_days_sign = 0
        else:
            diff_sell_price_three_days = round((actual_sell_price - sell_price_three_days_ago), 2)
            three_days_sign = assign_sign_to_sell_price(diff_sell_price_three_days)

        if sell_price_week_ago == 0:
            diff_sell_price_week =0
            week_sign = 0
        else:
            diff_sell_price_week = round((actual_sell_price - sell_price_week_ago), 2)
            week_sign = assign_sign_to_sell_price(diff_sell_price_week)

        if sell_price_month_ago == 0:
            diff_sell_price_month = 0
            month_sign = 0
        else:
            diff_sell_price_month = round((actual_sell_price - sell_price_month_ago), 2)
            month_sign = assign_sign_to_sell_price(diff_sell_price_month)
  # Записываем полученные данные в таблицу (записываем абсолютные значения, а признак + или - пишем отдельным значением)
        cursor.execute(f"INSERT INTO difference_sell_price VALUES (Null, '{api_id}', '{name2}', '{rarity}', '{actual_sell_price}', '{one_day_sign}', '{abs(diff_sell_price_one_day)}', '{three_days_sign}', '{abs(diff_sell_price_three_days)}', '{week_sign}', '{abs(diff_sell_price_week)}', '{month_sign}', '{abs(diff_sell_price_month)}')")
        conn.commit()


if __name__ == '__main__':
    try:
        while True:
            check_tables()
            api_data_recording()
            remove_old_data_from_all_collected_data()
            collect_diff_data_to_bd()
            time.sleep(240)
    except KeyboardInterrupt:
        print('Вы завершили работу программы collector')
        logger.info('Program has been stop manually')
    except Exception as e:
        t_alarmtext = f'Crossout_helper (app_collector.py): {str(e)}'
        do_alarm(t_alarmtext)
        logger.error(f'Other except error Exception', exc_info=True)