import sys

from loguru import logger
from config.settings import LOG_FILE, LOG_LEVEL, LOG_FORMAT


def setup_logging():
    logger.remove()  # Удаляем стандартный обработчик
    logger.add(
        LOG_FILE,
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        rotation="10 MB",  # Ротация по размеру файла
        compression="zip",  # Сжатие старых логов
        backtrace=True,     # Включаем трассировку для ошибок
        diagnose=True       # Включаем диагностику для ошибок
    )

    # Добавляем обработчик для вывода в консоль
    logger.add(
        sys.stdout,
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        colorize=True       # Включаем цветной вывод в консоль
    )

    logger.info(">>> Logging initialized")
    return logger