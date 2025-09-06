from aiogram import Dispatcher
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.markdown import hbold
from loguru import logger

from core.states import UploadForm


# Создаем клавиатуру для выбора съемки
def get_shooter_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Shoot 1"), KeyboardButton(text="Shoot 2")],
            [KeyboardButton(text="Shoot 3"), KeyboardButton(text="Shoot 4")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

# Соответствие текста кнопок внутренним идентификаторам
SHOOTER_MAPPING = {
    "Shoot 1": "shooter_1",
    "Shoot 2": "shooter_2", 
    "Shoot 3": "shooter_3",
    "Shoot 4": "shooter_4"
}


def register_handlers(dp: Dispatcher, process_help_command=None):
    # Команда /start
    dp.message.register(
        process_start_command,
        CommandStart(),
        StateFilter(default_state)
    )

    # Команда /help
    dp.message.register(
        process_help_command,
        Command(commands='help'),
        StateFilter(default_state)
    )

    # Команда /cancel
    dp.message.register(
        process_cancel_command_state,
        Command(commands='cancel')
    )

    # Обработка выбора съемки из клавиатуры
    dp.message.register(
        process_shooter_selection,
        StateFilter(UploadForm.select_shooter)
    )

    # Обработка неизвестных сообщений в начальном состоянии
    dp.message.register(
        handle_unknown_messages,
        StateFilter(default_state)
    )


async def process_start_command(message: Message, state: FSMContext):
    logger.info("Command START received")
    
    # Переходим в состояние выбора съемки
    await state.set_state(UploadForm.select_shooter)
    
    await message.answer(
        text='Добро пожаловать! Этот бот помогает добавлять фото в архив\n\n'
             'Пожалуйста, выберите съемку:',
        reply_markup=get_shooter_keyboard()
    )


async def process_shooter_selection(message: Message, state: FSMContext):
    selected_shooter = message.text
    
    # Проверяем, что выбран валидный стрелок
    if selected_shooter not in SHOOTER_MAPPING:
        await message.answer(
            text='Пожалуйста, выберите стрелка из предложенных вариантов:',
            reply_markup=get_shooter_keyboard()
        )
        return
    
    # Сохраняем выбранного стрелка в состоянии
    internal_shoot_id = SHOOTER_MAPPING[selected_shooter]
    await state.update_data(internal_shoot_id=internal_shoot_id)
    
    logger.info(f"Selected shooter: {internal_shoot_id}")
    
    # Переходим к следующему шагу или завершаем выбор
    await message.answer(
        text=f'Выбран стрелок: {selected_shooter}\n\n'
             'Чтобы перейти к отправке фото - '
             'отправьте команду /add_image',
        reply_markup=None  # Убираем клавиатуру
    )
    
    # Возвращаемся в default_state или переходим к следующему состоянию
    await state.set_state(default_state)


async def process_cancel_command_state(message: Message, state: FSMContext):
    logger.info("Command CANCEL received")
    current_state = await state.get_state()

    if current_state == UploadForm.select_shooter:
        # Если отменяем во время выбора стрелка
        await message.answer(
            text='Выбор стрелка отменен\n\n'
                 'Чтобы начать заново, отправьте команду /start',
            reply_markup=None
        )
    elif current_state is None:
        await message.answer(
            text='Нечего отменять. Вы не выполняете никаких операций.\n'
                 'Чтобы начать загрузку фото, отправьте команду /add_image'
        )
        return
    else:
        await message.answer(
            text='Вы прервали работу\n\n'
                 'Чтобы вернуться к загрузке фото\n '
                 'отправьте команду\n/add_image'
        )
    
    # Сбрасываем состояние и очищаем данные
    await state.clear()


async def handle_unknown_messages(message: Message):
    logger.info("Handling unknown message")
    await message.answer(
        f"{hbold(message.from_user.full_name)}\n"
        f"для начала работы\n"
        f"отправьте команду\n/start\n"
        f"Чтобы загрузить фото\n"
        f"отправьте команду\n/add_image\n"
    )
