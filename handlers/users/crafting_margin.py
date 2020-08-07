import logging
from src.selector import _get_top5_crafting
from aiogram.dispatcher import FSMContext
from loader import dp, bot
from states.crafting_margin import CraftingMargin
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from keyboards.inline.callback_datas import menu_callbacks
from keyboards.inline.choice_buttons import start_menu, crafting_margin_choise_rare
from src.analyzer import insert_in_analyz_table


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dp.message_handler(Command('start'), state='*')
async def show_start_menu(message: Message):
    text = 'Привет. \nЯ помогу тебе поднять золотишка! \nВыбирай кнопку'
    await message.answer(text=text, reply_markup=start_menu)
    await CraftingMargin.first()

    insert_in_analyz_table(message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username, button='start')


@dp.callback_query_handler(menu_callbacks.filter(click1='crafting_margin'), state=CraftingMargin.Start)  # Ловим State
async def crafting_margin(call: CallbackQuery, state: FSMContext):
    await state.get_state()
    # Укажем cache_time, чтобы бот не получал какое-то время апдейты, тогда нижний код не будет выполняться.
    # Отобразим что у нас лежит в callback_data
    #logger.info(f'callback_data_type={call.data.split(":")[1]}')  # Задаю разделитель ":" и вывел второй элемент массива

    text = 'Выбери редкость деталей'
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text)  # Меняем текст в сообщении
    await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=crafting_margin_choise_rare)  # Меняем клавиатуру в сообщении
    await CraftingMargin.next()  # Присваиваем состояние что переходит на выбор редкости

    insert_in_analyz_table(call.from_user.id, call.from_user.first_name, call.from_user.last_name,
                           call.from_user.username, call.data.split(':')[1])


@dp.callback_query_handler(state=CraftingMargin.ChoiseRarity)
async def choice_rarity(call: CallbackQuery, state: FSMContext):
    button_callback = call.data.split(":")[1]
    logger.info(f'button_callback={button_callback}')
    logger.info(f'callback_data={call.data}')
    if button_callback != 'Back':
        await call.message.answer(text=f'{_get_top5_crafting(button_callback)}', reply_markup=ReplyKeyboardRemove())
    else:
        text = 'Привет. \nЯ помогу тебе поднять золотишка!\nВыбирай кнопку'
        await call.message.answer(text=text, reply_markup=start_menu)  # Отправляем стартовое меню
        await state.get_state()
        await CraftingMargin.first()  # Меняем состояние на первое

        insert_in_analyz_table(call.from_user.id, call.from_user.first_name, call.from_user.last_name,
                               call.from_user.username, call.data.split(':')[1])


## You can use state '*' if you need to handle all states
#@dp.message_handler(menu_callbacks.filter(click1="Back"), state='*')
#async def cancel_handler(call: CallbackQuery, state: FSMContext):
#    """
#    Allow user to cancel any action
#    """
#    current_state = await state.get_state()
#    if current_state is None:
#        return
#
#    logging.info('Back state %r', current_state)
#    # Cancel state and inform user about it
#    await CraftingMargin.previous()
#    # And remove keyboard (just in case)
#    await call.message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


#@dp.message_handler(Command("test"), state=None)
#async def enter_test(message: types.Message):
#    await message.answer("Вы начали тестирование.\n"
#                         "Вопрос №1. \n\n"
#                         "Вы часто занимаетесь бессмысленными делами "
#                         "(бесцельно блуждаете по интернету, клацаете пультом телевизора, просто смотрите в потолок)?")
#
#    # Вариант 1 - с помощью функции сет
#    await CraftingMargin.ChoiseRarity.set()
#
#    # Вариант 2 - с помощью first
#    # await Test.first()
#
#
#
#    # Ваирант 2 получения state (если надо будет присвоить state другому пользователю, либо получить state от другого пользователя)
#    # state = dp.current_state(chat=message.chat.id, user=message.from_user.id)
#
#    # Вариант 1 сохранения переменных - записываем через key=var
#    await state.update_data(answer1=answer)
#
#    # Вариант 2 - передаем как словарь
#    await state.update_data(
#        {"answer1": answer}
#    )
#
#    # Вариант 3 - через state.proxy
#    #async with state.proxy() as data:
#    #    data["answer1"] = answer
#    #    # Удобно, если нужно сделать data["some_digit"] += 1
#    #    # Или data["some_list"].append(1), т.к. не нужно сначала доставать из стейта, А потом задавать
#
#    await message.answer("Вопрос №2. \n\n"
#                         "Ваша память ухудшилась и вы помните то, что было давно, но забываете недавние события?")
#
#
#
#@dp.message_handler(state=CraftingMargin.ChoiseFaction)
#async def answer_q2(message: types.Message, state: FSMContext):
#    # Достаем переменные
#    data = await state.get_data()
#    answer1 = data.get("answer1")
#    answer2 = message.text
#
#    await message.answer("Спасибо за ваши ответы!")
#
#    # Вариант 1
#    await state.finish()
#
#    # Вариант завершения 2
#    # await state.reset_state()
#
#    # Вариант завершения 3 - без стирания данных в data
#    # await state.reset_state(with_data=False)
