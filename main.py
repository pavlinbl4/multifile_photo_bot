import asyncio
import sys

from loguru import logger

from core.bot import setup_bot, register_all_handlers, setup_bot_commands
from services.selenium_service import selenium_worker


async def main():


    # Настройка и запуск бота
    bot, dp = setup_bot()
    logger.info('Bot started')

    # Регистрация обработчиков и команд
    register_all_handlers(dp)

    # Устанавливаем команды бота
    await setup_bot_commands(bot)

    # Запускаем воркер для обработки задач Selenium
    selenium_task = asyncio.create_task(selenium_worker(bot))

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
        # Проверяем версию Python
        if sys.version_info < (3, 8):
            logger.error("❌ Требуется Python 3.8 или выше")
            sys.exit(1)

        # Запускаем бота
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
