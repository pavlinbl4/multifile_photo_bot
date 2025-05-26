from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from config.settings import TOKEN

def setup_bot():
    """Настройка бота и диспетчера"""
    # Инициализируем хранилище
    storage = MemoryStorage()

    # Инициализация бота с настройками
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )

    # Инициализация диспетчера с хранилищем
    dp = Dispatcher(storage=storage)

    logger.info("Bot and dispatcher initialized")
    return bot, dp


# Функция для установки команд бота
async def setup_bot_commands(bot: Bot):
    """Установка команд бота"""
    from config.bot_commands import get_commands

    commands = get_commands()
    await bot.set_my_commands(commands)
    logger.info("Bot commands have been set")


# Функция для регистрации всех обработчиков
def register_all_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    from handlers.upload import register_handlers as register_upload_handlers
    from handlers.common import register_handlers as register_common_handlers

    register_upload_handlers(dp)
    register_common_handlers(dp)
    logger.info("All handlers have been registered")