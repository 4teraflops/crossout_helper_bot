import sqlite3
from datetime import datetime, timedelta


one_day_ago_time = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
one_day_ago_time_allowence = (datetime.now() - timedelta(days=1) + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")

three_days_ago_time = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
three_days_ago_time_allowence = (datetime.now() - timedelta(days=3) + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")

week_ago_time = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
week_ago_time_allowence = (datetime.now() - timedelta(days=7) + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")

month_ago_time = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
month_ago_time_allowence = (datetime.now() - timedelta(days=30) + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")

# Инициируем подключение к БД
db_path = 'src/db.sqlite'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()


def get_sell_price_from_historycal_data(api_id, start_time, end_time):
    price = cursor.execute(f"SELECT sell_price from all_collected_data WHERE operation_time >= '{start_time}' AND operation_time <= '{end_time}' AND api_id = '{api_id}' LIMIT 1").fetchall()
    # если данные не найдены, то присваиваем значение 'None'
    try:
        price = price[0][0]
    except IndexError:
        price = 'None'
    conn.commit()
    # если загрузилось пустое множество, то тоже присваиваем none
    if price:
        return price
    else:
        return 'None'

api_ids = cursor.execute("SELECT api_id from actual_data").fetchall()

for api_id in api_ids:
    api_id = api_id[0]
    # Получил данные из таблицы
    name2 = cursor.execute(f'SELECT name2 FROM actual_data WHERE api_id = "{api_id}"').fetchall()[0][0]
    rarity = cursor.execute(f'SELECT rarity FROM actual_data WHERE api_id = "{api_id}"').fetchall()[0][0]
    actual_sell_price = cursor.execute(f'SELECT sell_price FROM actual_data WHERE api_id = "{api_id}"').fetchall()[0][0]

    sell_price_one_day_ago = get_sell_price_from_historycal_data(api_id, one_day_ago_time, one_day_ago_time_allowence)
    sell_price_three_days_ago = get_sell_price_from_historycal_data(api_id, three_days_ago_time, three_days_ago_time_allowence)
    sell_price_week_ago = get_sell_price_from_historycal_data(api_id, week_ago_time, week_ago_time_allowence)
    sell_price_month_ago = get_sell_price_from_historycal_data(api_id, month_ago_time, month_ago_time_allowence)
    # Посчитал разницу (на случай, если одна из цен отсутствует, сделал исключение, чтоб выводил что нет данных)
    try:
        diff_sell_price_one_day = round((actual_sell_price - sell_price_one_day_ago), 2)
    except TypeError:
        diff_sell_price_one_day = 'No data'
    try:
        diff_sell_price_three_days = round((actual_sell_price - sell_price_three_days_ago), 2)
    except TypeError:
        diff_sell_price_three_days = 'No data'
    try:
        diff_sell_price_week = round((actual_sell_price - sell_price_week_ago), 2)
    except TypeError:
        diff_sell_price_week = 'No data'
    try:
        diff_sell_price_month = round((actual_sell_price - sell_price_month_ago), 2)
    except TypeError:
        diff_sell_price_month = 'No data'

    print(name2, '|', actual_sell_price, '|', diff_sell_price_one_day, '|', diff_sell_price_three_days, diff_sell_price_week, '|', diff_sell_price_month)

