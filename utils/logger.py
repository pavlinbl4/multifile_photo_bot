from loguru import logger
from config.settings import LOG_FILE, LOG_LEVEL, LOG_FORMAT


def setup_logging():
    logger.remove()  # Удаляем стандартный обработчик
    logger.add(
        LOG_FILE,
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        rotation="10 MB",  # Ротация по размеру файла
        compression="zip"  # Сжатие старых логов
    )

    logger.info(">>> Logging initialized")
    return logger