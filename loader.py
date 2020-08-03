import importlib
import logging
import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Храним чувствительные данные в переменной окружения
# Это значение по умолчанию на случай, если переменной окружения не будет
os.environ.setdefault('SETTINGS_MODULE', 'config')
# Импортируем модуль, указанный в переменной окружения
config = importlib.import_module(os.getenv('SETTINGS_MODULE'))
# Параметры для прокси
PROXY_AUTH = aiohttp.BasicAuth(login=config.PROXY_USER, password=config.PROXY_PASS)
bot = Bot(config.token, proxy=config.PROXY_URL, proxy_auth=PROXY_AUTH, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )
logger = logging.getLogger(__name__)
