from aiogram import F, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from loguru import logger

from core.states import UploadForm
from services.file_service import (
    save_file_to_disk,
    convert_to_jpeg_if_needed,
    is_valid_file,
    prepare_upload_path
)
from services.selenium_service import add_upload_task
from services.security import is_user_allowed, log_unauthorized_access
from config.settings import MIN_CREDIT_LENGTH


def register_handlers(dp: Dispatcher):
    # Команда /add_image для авторизованных пользователей
    dp.message.register(
        process_add_image_command,
        Command(commands='add_image'),
        StateFilter(default_state),
        F.from_user.username.func(is_user_allowed)
    )

    # Команда /add_image для неавторизованных пользователей
    dp.message.register(
        handle_unauthorized_user,
        Command(commands='add_image'),
        StateFilter(default_state)
    )

    # Обработка ввода кредита (корректная длина)
    dp.message.register(
        process_credit_sent,
        StateFilter(UploadForm.add_credit),
        F.text.len() >= MIN_CREDIT_LENGTH
    )

    # Обработка ввода кредита (некорректная длина)
    dp.message.register(
        process_invalid_credit,
        StateFilter(UploadForm.add_credit),
        F.text.len() < MIN_CREDIT_LENGTH
    )

    # Обработка загрузки файла
    dp.message.register(
        handle_file_upload,
        StateFilter(UploadForm.add_file)
    )


async def process_add_image_command(message: Message, state: FSMContext):
    logger.info("Command ADD_IMAGE received from authorized user")
    await message.answer(text="Укажите автора/правообладателя снимка")
    # Устанавливаем состояние ожидания ввода кредита
    await state.set_state(UploadForm.add_credit)


async def handle_unauthorized_user(message: Message):
    logger.warning(f"Unauthorized user tried to use the bot: {message.from_user.full_name}")
    log_unauthorized_access(message.from_user)
    await message.answer(
        f"Извините, {hbold(message.from_user.full_name)}\n"
        f"это частный бот и вы не включены в "
        f"список пользователей."
    )


async def process_credit_sent(message: Message, state: FSMContext):
    logger.info(f"Credit received: {message.text}")
    # Сохраняем введенное имя в хранилище
    await state.update_data(credit=message.text)
    await message.answer(text='Спасибо!\n\nА теперь загрузите снимки как файл')
    # Переходим к состоянию загрузки файла
    await state.set_state(UploadForm.add_file)


async def process_invalid_credit(message: Message, state: FSMContext):
    logger.warning(f"Invalid credit received: {message.text}")
    await message.answer(
        text=f'Текст должен быть не короче {MIN_CREDIT_LENGTH} символов'
    )
    # Остаемся в состоянии ввода кредита
    await state.set_state(UploadForm.add_credit)


async def process_single_file(file, message: Message, state: FSMContext):
    try:
        if not is_valid_file(file.mime_type):
            await message.answer(
                f"Вы отправили недопустимый тип файла: {file.mime_type}\n"
                f"Я работаю только с фотографиями."
            )
            return

        file_id = file.file_id
        file_obj = await message.bot.get_file(file_id)
        file_path = file_obj.file_path

        # Подготавливаем путь для сохранения файла
        destination_path = prepare_upload_path(file.file_name)

        # Сохраняем файл
        saved_path = await save_file_to_disk(message.bot, file_path, str(destination_path))

        # Конвертируем в JPEG при необходимости
        final_path = convert_to_jpeg_if_needed(saved_path)

        # Получаем кредит из состояния
        data = await state.get_data()
        credit = data.get("credit", "Unknown")

        # Добавляем задачу в очередь
        await add_upload_task(final_path, file.file_name, credit, message.chat.id)

        await message.answer(
            text=f'Файл {file.file_name} принят в обработку. Ожидайте завершения.'
        )

    except Exception as e:
        logger.error(f"Error processing file {file.file_name}: {e}")
        await message.answer(
            f"Произошла ошибка при обработке файла {file.file_name}: {e}"
        )


async def handle_file_upload(message: Message, state: FSMContext):
    logger.debug("File upload handler triggered")

    if message.document is None:
        logger.debug("Photo was sent as PHOTO, not as file")
        await message.answer(
            "Отправьте фото «как файл», чтобы сохранить качество снимка"
        )
        return

    # Обрабатываем один или несколько файлов
    files = message.document if isinstance(message.document, list) else [message.document]

    for file in files:
        await process_single_file(file, message, state)