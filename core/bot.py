from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from config.settings import TOKEN

# Инициализируем хранилище
storage = MemoryStorage()

# Создаем объекты бота и диспетчера
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)


# Функция для установки команд бота
async def setup_bot_commands():
    from config.bot_commands import COMMANDS
    await bot.set_my_commands(COMMANDS)


# Функция для регистрации всех обработчиков
def register_all_handlers():
    from handlers.upload import register_handlers as register_upload_handlers
    from handlers.common import register_handlers as register_common_handlers

    register_upload_handlers(dp)
    register_common_handlers(dp)
