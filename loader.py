import importlib
import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru import logger

# Храним чувствительные данные в переменной окружения
# Это значение по умолчанию на случай, если переменной окружения не будет
os.environ.setdefault('SETTINGS_MODULE', 'config')
# Импортируем модуль, указанный в переменной окружения
config = importlib.import_module(os.getenv('SETTINGS_MODULE'))
# Параметры для прокси
#PROXY_AUTH = aiohttp.BasicAuth(login=config.PROXY_USER, password=config.PROXY_PASS)
bot = Bot(config.token, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logger.add(f'src/log/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')
