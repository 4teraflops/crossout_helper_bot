from aiogram.dispatcher.filters.state import StatesGroup, State


class CraftingMargin(StatesGroup):
    Start = State()
    ChoiseRarity = State()