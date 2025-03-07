from pathlib import Path

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from loguru import logger

from get_credentials import Credentials
from check_existing_file import create_dir
from common.bot_commands_list import kp_uploader

import asyncio

from image_converter.conver_image_to_jpeg import convert_image_to_jpeg
from photo_uplolader.shlack_uploader import web_photo_uploader

# Создаем очередь для задач Selenium
selenium_queue = asyncio.Queue()
results_queue = asyncio.Queue()

# Включаем логирование, чтобы не пропустить важные сообщения
logger.add("photo_uploader.log", level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

# TOKEN = Credentials().contraption_bot
TOKEN = Credentials().pavlinbl4_bot
logger.info("Used pavlinbl4_bot")

ALLOWED_USER_NAMES = {"PavlenkoEV"}

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = MemoryStorage()

# Создаем объекты бота и диспетчера
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)
logger.info(">>> Запуск бота...")

"""функция, которая будет проверять очередь результатов и отправлять сообщения пользователю:"""
# async def process_results():
#     while True:
#         # Получаем результат из очереди
#         task, result = await results_queue.get()
#         logger.debug(f"Processing result: {result}")
#
#         # Извлекаем данные из задачи
#         file_path, file_name, credit = task
#         user_message = f"Файл {file_name} обработан. Результат: {result}"
#
#         # Отправляем сообщение пользователю
#         # Здесь нужно получить chat_id, например, из состояния (state) или другого источника
#         # В вашем случае, можно передавать chat_id вместе с задачей
#         chat_id = task[3]  # Пример: chat_id передается как часть задачи
#         await bot.send_message(chat_id, user_message)
#
#         # Помечаем результат как обработанный
#         results_queue.task_done()

# создаю воркер для отправки файлов
async def selenium_worker():
    while True:
        # Получаем задачу из очереди
        logger.debug(f"Selenium_worker started")
        task = await selenium_queue.get()
        logger.debug(f"Processing file in worker: {task}")

        try:
            # Проверяем, что задача содержит все необходимые элементы
            if not isinstance(task, (list, tuple)) or len(task) != 4:
                logger.error(f"Invalid task format: {task}")
                continue  # Пропускаем некорректную задачу

            # Распаковываем данные задачи
            file_path, file_name, credit, chat_id = task
            logger.debug(f"file_path: {file_path}, file_name: {file_name}, chat_id: {chat_id}")

            # Выполняем задачу
            result = await asyncio.to_thread(web_photo_uploader, file_path, file_name, credit)
            logger.debug(f"Task completed: {result}")

            # Отправляем результат пользователю
            await bot.send_message(chat_id, f"Файл {file_name} обработан. Результат: {result}")
        except Exception as e:
            logger.error(f"Error in selenium_worker: {e}")
            # Отправляем сообщение об ошибке
            if 'chat_id' in locals():  # Проверяем, что chat_id был определен
                await bot.send_message(chat_id, f"Ошибка при обработке файла {file_name}: {e}")
        finally:
            # Помечаем задачу как выполненную
            logger.debug(f"Processing file in worker: Task done")
            selenium_queue.task_done()


def is_allowed_file_type(mime_type: str) -> bool:
    allowed_files_type = {'image/jpeg', 'image/png', 'image/x-tiff'}
    return mime_type in allowed_files_type


async def save_file_to_disk(file_path: str, destination_path: str) -> None:
    await bot.download_file(file_path, destination_path)


def convert_to_jpeg_if_needed(file_path: str) -> str:
    if Path(file_path).suffix.lower() not in ['.jpeg', '.jpg']:
        return convert_image_to_jpeg(file_path)
    return file_path


class FSMFillForm(StatesGroup):
    add_file = State()  # Состояние ожидания добавления файла
    add_credit = State()  # Состояние ожидания ввода image credit


# handler_01 будет срабатывать на команду /start вне состояний
# и предлагать отправить фото, отправив команду /add_image
@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    logger.info("handler_01 work command START received")
    await message.answer(
        text='Этот бот помогает добавлять фото в архив\n\n'
             'Чтобы перейти к отправке фото - '
             'отправьте команду /add_image'
    )


# handler_02_1 будет срабатывать на команду "/help"
@dp.message(Command(commands='help'), StateFilter(default_state))
async def process_help_command(message: Message):
    logger.info("handler_02_1 work command HELP received")
    await message.answer(
        text='Этот бот помогает добавлять фото в архив\n\n'
             'Чтобы перейти к отправке фото\n'
             'отправьте команду /add_image\n'
             f'без указания автора фото бот работать не будет!!!'
    )


# handler_02_2 будет срабатывать на команду "/cancel" в любых состояниях,
@dp.message(Command(commands='cancel'))
async def process_cancel_command_state(message: Message, state: FSMContext):
    logger.info("handler_02_2 work command CANCEL received")
    await message.answer(
        text='Вы прервали работу\n\n'
             'Чтобы вернуться к загрузке фото\n '
             'отправьте команду\n/add_image'
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# handler_03 будет срабатывать на команду /add_image
# в новой версии вначале хочу получить данные о правообладателе

@dp.message(Command(commands='add_image'), StateFilter(default_state), F.from_user.username.in_(ALLOWED_USER_NAMES))
async def process_add_image_command(message: Message, state: FSMContext):
    logger.info("handler_03 work command ADD_IMAGE received")
    await message.answer(text="Укажите автора/правообладателя снимка")
    logger.info("Запрос кредитов на снимок")
    # Устанавливаем состояние ожидания ввода кредита
    await state.set_state(FSMFillForm.add_credit)


async def process_single_file(uploaded_file: types.Document, message: types.Message, state: FSMContext) -> None:
    try:
        file_id = uploaded_file.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path

        uploaded_images = create_dir("Uploaded_images")

        logger.info(f'{uploaded_file.file_name = }')
        path_to_uploaded_image = f"{uploaded_images}/{uploaded_file.file_name}"
        path_to_uploaded_image = convert_to_jpeg_if_needed(path_to_uploaded_image)

        await save_file_to_disk(file_path, path_to_uploaded_image)

        # Получаем данные о кредите из состояния
        data = await state.get_data()
        credit = data.get("credit", "Unknown")

        # Создаем задачу
        task = (path_to_uploaded_image, uploaded_file.file_name, credit, message.chat.id)
        logger.debug(f"Adding task to queue: {task}")

        # Добавляем задачу в очередь
        await selenium_queue.put(task)

        logger.debug(f"Файл {uploaded_file.file_name} ({path_to_uploaded_image}) добавлен в очередь Selenium")
        await message.answer(text=f'Файл {uploaded_file.file_name} принят в обработку. Ожидайте завершения.')

    except Exception as e:
        logger.error(f"Error processing file {uploaded_file.file_name}: {e}")
        await message.answer(
            f"Произошла ошибка при обработке файла {uploaded_file.file_name}. Пожалуйста, попробуйте еще раз.")


# handler_04 будет срабатывать, если отправлено фото
# и переводить в состояние ожидания ввода автора фото
@dp.message(StateFilter(FSMFillForm.add_file))
async def handle_allowed_user_messages(message: types.Message, state: FSMContext):
    # logger.info("handler_04 work - file send")
    # logger.debug(message.document)
    # если message.document is None - значит прислали не файл и не медиа группу
    if message.document is None:
        logger.debug("Photo was send as PHOTO not file")
        await message.answer(f"Отправьте фото «как файл», чтоб сохранить качество\n"
                             f"снимка")
        await state.set_state(FSMFillForm.add_file)

    else:
        uploaded_files = message.document if isinstance(message.document, list) else [message.document]
        logger.debug(f'{uploaded_files = }')
        for uploaded_file in uploaded_files:
            if is_allowed_file_type(uploaded_file.mime_type):
                await process_single_file(uploaded_file, message, state)
            else:
                await message.answer(f"Вы отправили недопустимый тип файла\n"
                                     f"{uploaded_file.mime_type}\n"
                                     f"я работаю только с фотографиями")
                await state.set_state(FSMFillForm.add_file)


# handler_05 будет срабатывать, если введен корректный кредит
# и переводить в состояние ожидания добавления снимка/снимков
@dp.message(StateFilter(FSMFillForm.add_credit), F.text.len() > 3)
async def process_name_sent(message: Message, state: FSMContext):
    logger.debug("handler_05 work CREDIT received")
    # сохраняем введенное имя в хранилище по ключу "credit"
    await state.update_data(credit=message.text)
    await message.answer(text='Спасибо!\n\nА теперь загрузите снимки как файл')
    await state.set_state(FSMFillForm.add_file)


# handler_06
@dp.message(Command(commands='add_image'), StateFilter(default_state))
async def handle_other_messages(message: types.Message):
    logger.info("handler_06 work")
    # This function will be called for messages from any other user
    with open('kp_photo_uploader_bot/users.txt', 'a') as txt_user_base:
        txt_user_base.write(f'{message.from_user.full_name} - {message.from_user.id}\n')
    await message.answer(f"Извините, {hbold(message.from_user.full_name)}\n"
                         f"это частный бот и вы не включены в"
                         f"список пользователей .")


# handler_07 будет срабатывать, если введено корректное автора/правообладателя
# и переводить в состояние ожидания добавления файла
@dp.message(StateFilter(FSMFillForm.add_credit), F.text.len() < 3)
async def process_credit_sent(message: Message, state: FSMContext):
    logger.info("handler_07 work")
    # сохраняем введенное имя в хранилище по ключу "credit"
    await state.update_data(credit=message.text)
    await message.answer(text='текст не может быть короче 3 букв')
    # Устанавливаем состояние ожидания добавления файла
    await state.set_state(FSMFillForm.add_file)


# handler_08
@dp.message(StateFilter(default_state))
async def handle_other_messages_2(message: types.Message):
    logger.info("handler_08 work")
    # This function will be called for messages from any other user
    await message.answer(f"{hbold(message.from_user.full_name)}\n"
                         f"для начала работы\n"
                         f"отправьте команду\n/start\n"
                         f"Чтобы загрузить фото\n"
                         f"отправьте команду\n/add_image\n")


# start polling
if __name__ == '__main__':
    async def set_main_menu():
        await bot.set_my_commands(commands=kp_uploader)

    async def main():
        # Запускаем воркер для обработки задач Selenium
        asyncio.create_task(selenium_worker())

        # Устанавливаем команды бота
        await set_main_menu()

        # Запускаем бота
        await dp.start_polling(bot)

    # Запуск основного цикла
    asyncio.run(main())