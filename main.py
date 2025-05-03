import asyncio
from loguru import logger

from core.bot import bot, dp, setup_bot_commands, register_all_handlers
from utils.logger import setup_logging
from services.selenium_service import selenium_worker


async def main():
    # Настраиваем логирование
    setup_logging()
    logger.info(">>> Starting bot...")

    # Регистрируем все обработчики
    register_all_handlers()

    # Устанавливаем команды бота
    await setup_bot_commands()

    # Запускаем воркер для обработки задач Selenium
    selenium_task = asyncio.create_task(selenium_worker())

    try:
        # Запускаем бота
        await dp.start_polling(bot)
    finally:
        # Закрываем соединения
        await bot.session.close()
        # Останавливаем воркер корректно
        selenium_task.cancel()

        try:
            await selenium_task
        except asyncio.CancelledError:
            pass


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")