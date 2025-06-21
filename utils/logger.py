import sys

from loguru import logger

from config.settings import LOG_FILE, LOG_FORMAT, LOG_CONSOLE_LEVEL, LOG_FILE_LEVEL


def setup_logging():
    # Добавляем обработчик для вывода в файл
    logger.add(
        LOG_FILE,
        level=LOG_FILE_LEVEL,  # Уровень для файла
        format=LOG_FORMAT,
        rotation="10 MB",
        compression="zip",
        backtrace=True,
        diagnose=True
    )

    # Добавляем обработчик для вывода в консоль
    logger.add(
        sys.stdout,
        level=LOG_CONSOLE_LEVEL,  # Уровень для консоли
        format=LOG_FORMAT,
        colorize=True
    )

    logger.info(">>> Logging initialized")
    return logger
