from loguru import logger
from src.selector import get_top_10_difference_prices
from aiogram.dispatcher import FSMContext
from loader import dp, bot
from states.crafting_margin import CraftingMargin
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from keyboards.inline.callback_datas import menu_callbacks
from keyboards.inline.choice_buttons import difference_prices_choise_time_range, start_menu
from src.analyzer import insert_in_analyz_table


logger.add(f'src/log/{__name__}.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')


@dp.callback_query_handler(menu_callbacks.filter(click1='difference_prices'), state=CraftingMargin.Start)  # Ловим State
async def crafting_margin(call: CallbackQuery, state: FSMContext):
    await state.get_state()
    # Укажем cache_time, чтобы бот не получал какое-то время апдейты, тогда нижний код не будет выполняться.
    # Отобразим что у нас лежит в callback_data
    #logger.debug(f'callback_data_type={call.data.split(":")[1]}')  # Задаю разделитель ":" и вывел второй элемент массива
    text = 'Выбери временной диапазон'
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text)  # Меняем текст в сообщении
    await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=difference_prices_choise_time_range)  # Меняем клавиатуру в сообщении
    await CraftingMargin.DiffStart.set()  # Присваиваем актуальное состояние
    # В анализ
    insert_in_analyz_table(call.from_user.id, call.from_user.first_name, call.from_user.last_name,
                           call.from_user.username, call.data.split(':')[1])


@dp.callback_query_handler(state=CraftingMargin.DiffStart)
async def choise_time_range(call: CallbackQuery, state: FSMContext):
    button_callback = call.data.split(":")[1]
    if button_callback == 'Back':
        text = 'Привет. \nЯ помогу тебе поднять золотишка!\nВыбирай кнопку'
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text)
        await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=start_menu)
        await state.get_state()
        await CraftingMargin.first()  # Меняем состояние на первое
        # В анализ
        insert_in_analyz_table(call.from_user.id, call.from_user.first_name, call.from_user.last_name,
                               call.from_user.username, call.data.split(':')[1])
    else:
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=get_top_10_difference_prices(time=f'{button_callback}'))
        await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=difference_prices_choise_time_range)
        await state.get_state()
        await CraftingMargin.DiffStart.set()
        # В анализ
        insert_in_analyz_table(call.from_user.id, call.from_user.first_name, call.from_user.last_name,
                               call.from_user.username, call.data.split(':')[1])