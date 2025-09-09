from aiogram import F, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from loguru import logger

from core.states import UploadForm
from handlers.common import process_cancel_command_state
from services.file_service import (
    save_file_to_disk,
    is_valid_file,
    prepare_upload_path
)
from services.image_service.conver_image_to_jpeg import convert_image_to_jpeg
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

    # Добавляем обработчик /cancel для состояния ввода кредита
    dp.message.register(
        process_cancel_command_state,
        Command(commands='cancel'),
        StateFilter(UploadForm.add_credit)
    )

    # Добавляем обработчик /cancel для состояния загрузки файлов
    dp.message.register(
        process_cancel_command_state,
        Command(commands='cancel'),
        StateFilter(UploadForm.add_file)
    )

    # Команда для завершения загрузки
    dp.message.register(
        finish_upload,
        Command(commands=['finish']),
        StateFilter(UploadForm.add_file)
    )

    # Текстовая команда для завершения загрузки
    dp.message.register(
        finish_upload,
        StateFilter(UploadForm.add_file),
        F.text.casefold() == "завершить"
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
    await message.answer(
        text='Спасибо!\n\nА теперь загрузите снимки как файл\n\n'
             'Когда закончите загрузку, отправьте команду /finish или напишите "Завершить"'
    )
    # Получаем данные из состояния
    data = await state.get_data()
    internal_shoot_id = data.get('internal_shoot_id')
    logger.debug(f'{internal_shoot_id = }')

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

        # конвертируем в JPEG и jpeg тоже так как бывает, что это webp
        final_path = convert_image_to_jpeg(saved_path)

        # Получаем кредит из состояния
        data = await state.get_data()
        credit = data.get("credit", "Unknown")

        internal_shoot_id = data.get('internal_shoot_id')
        logger.debug(f'Shoot number {internal_shoot_id = }')
        # Добавляем задачу в очередь
        await add_upload_task(final_path, file.file_name, credit, message.chat.id, internal_shoot_id)

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

    # Явная проверка на текстовые сообщения
    if not message.document and not message.photo:
        logger.debug("Non-file message received")
        await message.answer(
            "Пожалуйста, отправляйте фото как файлы.\n"
            "Для завершения отправьте /finish или 'Завершить'"
        )
        return

    # Обрабатываем один или несколько файлов
    files = message.document if isinstance(message.document, list) else [message.document]

    for file in files:
        await process_single_file(file, message, state)


async def finish_upload(message: Message, state: FSMContext):
    logger.info(f"User {message.from_user.full_name} completed file upload session")
    await message.answer(
        text="Загрузка файлов завершена. Спасибо!\n\n"
             "Если вам нужно загрузить еще снимки, используйте команду /add_image"
    )
    # Сбрасываем состояние и очищаем данные
    await state.clear()
