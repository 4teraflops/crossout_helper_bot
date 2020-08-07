from loader import bot, storage
import logging
from src.app_collector import do_alarm


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def on_shutdown(dp):
    await bot.close()
    await storage.close()


if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    try:

        executor.start_polling(dp, on_shutdown=on_shutdown)
    except KeyboardInterrupt:
        print('Вы завершили работу программы collector')
        logger.info('Program has been stop manually')
    except Exception as e:
        t_alarmtext = f'Crossout_helper (app.py): {str(e)}'
        do_alarm(t_alarmtext)
        logger.error(f'Other except error Exception', exc_info=True)
