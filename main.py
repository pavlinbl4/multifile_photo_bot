import asyncio
from loguru import logger

from core.bot import setup_bot_commands, register_all_handlers, setup_bot
from utils.logger import setup_logging
from services.selenium_service import selenium_worker, set_bot


async def main():
    # Настраиваем логирование
    setup_logging()

    # Объявляем переменные бота и диспетчера в области видимости функции
    bot = None
    dp = None

    try:
        # Запускаем бота
        bot, dp = setup_bot()
        logger.info('Bot started')

        # Устанавливаем команды бота
        await setup_bot_commands(bot)

        # Устанавливаем экземпляр бота для selenium_worker
        set_bot(bot)

        # Запускаем воркер для обработки задач Selenium
        selenium_task = asyncio.create_task(selenium_worker())

        # Регистрируем все обработчики
        register_all_handlers(dp)

        # Запускаем бота с опросом обновлений
        logger.info("Starting polling...")
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Critical error: {e}")
        raise
    finally:
        # Закрываем соединения только если бот был инициализирован
        if bot:
            logger.info("Closing bot session...")
            await bot.session.close()

        # Останавливаем воркер корректно - он должен быть определен в блоке try
        if 'selenium_task' in locals():
            logger.info("Cancelling selenium worker...")
            selenium_task.cancel()

            try:
                await selenium_task
            except asyncio.CancelledError:
                logger.info("Selenium worker stopped")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        exit(1)
