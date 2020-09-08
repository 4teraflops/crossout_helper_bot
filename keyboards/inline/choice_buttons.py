from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# from config import URL_APPLES, URL_PEAR
from keyboards.inline.callback_datas import menu_callbacks

# Вариант 1, как в прошлом уроке
# choice = InlineKeyboardMarkup(inline_keyboard=[
#     [
#         InlineKeyboardButton(text="Купить грушу", callback_data=buy_callback.new(item_name="pear")),
#         InlineKeyboardButton(text="Купить яблоки", callback_data="buy:apple")
#     ],
#     [
#         InlineKeyboardButton(text="Отмена", callback_data="next")
#     ]
# ])
## Вариант 2 - с помощью row_width и insert.
# choice = InlineKeyboardMarkup(row_width=2)
#
# buy_pear = InlineKeyboardButton(text="Купить грушу", callback_data=buy_callback.new(item_name="pear", quantity=1))
# choice.insert(buy_pear)
#
# buy_apples = InlineKeyboardButton(text="Купить яблоки", callback_data="buy:apple:5")
# choice.insert(buy_apples)
#
# cancel_button = InlineKeyboardButton(text="Отмена", callback_data="cancel")
# choice.insert(cancel_button)
#
## А теперь клавиатуры со ссылками на товары
# pear_keyboard = InlineKeyboardMarkup(inline_keyboard=[
#    [
#        InlineKeyboardButton(text="Купи тут", url=URL_APPLES)
#    ]
# ])
# apples_keyboard = InlineKeyboardMarkup(inline_keyboard=[
#    [
#        InlineKeyboardButton(text="Купи тут", url=URL_PEAR)
#    ]
# ])

start_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="ТОП 5 Крафтинг", callback_data=menu_callbacks.new(click1="crafting_margin")),
        InlineKeyboardButton(text="ТОП 10 скачков цен", callback_data=menu_callbacks.new(click1="difference_prices"))
    ]
])

crafting_margin_choise_rare = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Любая", callback_data='crafting_margin:All')
    ],
    [
        InlineKeyboardButton(text='Синие', callback_data='crafting_margin:Rare'),
        InlineKeyboardButton(text='Бирюза', callback_data='crafting_margin:Special')
    ],
    [
        InlineKeyboardButton(text="Фиолки", callback_data='crafting_margin:Epic'),
        InlineKeyboardButton(text="Леги", callback_data='crafting_margin:Legendary'),
        InlineKeyboardButton(text="Реликты", callback_data='crafting_margin:Relic')
    ],
    [
        InlineKeyboardButton(text="Назад", callback_data='crafting_margin:Back')
    ]
])

difference_prices_choise_time_range = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Сутки', callback_data='difference_prices:one_day'),
        InlineKeyboardButton(text='Три дня', callback_data='difference_prices:three_days')
    ],
    [
        InlineKeyboardButton(text='Неделя', callback_data='difference_prices:week'),
        InlineKeyboardButton(text='Месяц', callback_data='difference_prices:month')
    ],
    [
        InlineKeyboardButton(text="Назад", callback_data='difference_prices:Back')
    ]
])
