from aiogram import F, Dispatcher
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from loguru import logger


def register_handlers(dp: Dispatcher):
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

    # Обработка неизвестных сообщений в начальном состоянии
    dp.message.register(
        handle_unknown_messages,
        StateFilter(default_state)
    )


async def process_start_command(message: Message):
    logger.info("Command START received")
    await message.answer(
        text='Этот бот помогает добавлять фото в архив\n\n'
             'Чтобы перейти к отправке фото - '
             'отправьте команду /add_image'
    )


async def process_help_command(message: Message):
    logger.info("Command HELP received")
    await message.answer(
        text='Этот бот помогает добавлять фото в архив\n\n'
             'Чтобы перейти к отправке фото\n'
             'отправьте команду /add_image\n'
             'Без указания автора фото бот работать не будет!!!'
    )


async def process_cancel_command_state(message: Message, state: FSMContext):
    logger.info("Command CANCEL received")
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