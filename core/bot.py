from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from config.settings import TOKEN


def setup_bot():
    """
    Настройка бота и диспетчера

    Returns:
        tuple: Экземпляры бота и диспетчера
    """

    # Инициализируем хранилище
    storage = MemoryStorage()

    # Создаем объекты бота и диспетчера
    # logger.info(f'Token type: {type(TOKEN)}')
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Инициализация диспетчера
    dp = Dispatcher(storage=storage)

    # Добавляем обработчик для корректного завершения
    dp.shutdown.register(on_shutdown)

    logger.info("Bot and dispatcher initialized")
    return bot, dp


# Функция для установки команд бота
async def setup_bot_commands(bot: Bot):
    """
        Установка команд бота

        Args:
            bot: Экземпляр бота
        """
    from config.bot_commands import get_commands
    commands = get_commands()
    await bot.set_my_commands(commands)
    logger.info("Bot commands have been set")


# Функция для регистрации всех обработчиков
def register_all_handlers(dp: Dispatcher):
    from handlers.upload import register_handlers as register_upload_handlers
    from handlers.common import register_handlers as register_common_handlers

    register_upload_handlers(dp)
    register_common_handlers(dp)


async def on_shutdown(dispatcher: Dispatcher):
    """
    Обработчик события выключения бота

    Args:
        dispatcher: Экземпляр диспетчера
    """
    logger.info("Shutting down the bot...")

    # Закрываем соединения и освобождаем ресурсы
    await dispatcher.storage.close()

    logger.info("Bot has been shut down")
