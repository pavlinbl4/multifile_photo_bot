from aiogram.fsm.state import State, StatesGroup

class UploadForm(StatesGroup):
    add_credit = State()  # Состояние ожидания ввода image credit
    add_file = State()    # Состояние ожидания добавления файла