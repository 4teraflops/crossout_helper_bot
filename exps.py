from datetime import datetime, timedelta


data = '2020-05-05 11:00:18'
time = datetime.strptime(data, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=180)


actualtime = datetime.strftime((datetime.now() - timedelta(minutes=1440)), "%Y-%m-%d %H:%M:%S")

print(actualtime)
