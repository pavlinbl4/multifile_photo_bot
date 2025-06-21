import asyncio
from loguru import logger

from core.bot import setup_bot, register_all_handlers, setup_bot_commands
from services.selenium_service import selenium_worker


async def main():
    # Настраиваем логирование
    bot, dp = setup_bot()

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
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
