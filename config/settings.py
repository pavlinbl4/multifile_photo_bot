from pathlib import Path

from services.get_credentials import Credentials
from loguru import logger

# Пути к директориям
BASE_DIR = Path(__file__).parent.parent

UPLOADS_DIR = BASE_DIR / "Uploaded_images"

# Настройки бота
TOKEN = Credentials().crazypythonbot

logger.info(f'Now use crazypythonbot' if TOKEN.startswith('1579508574') else "Use other bot")
ALLOWED_USER_NAMES = {"PavlenkoEV"}
BASE_UPLOAD_LINK = 'https://image.kommersant.ru/photo/archive/adm/AddPhoto.aspx?shootid='

# Настройки обработки файлов
ALLOWED_FILE_TYPES = {'image/jpeg', 'image/png', 'image/x-tiff'}
MIN_CREDIT_LENGTH = 3

# Настройки логирования
LOG_FILE = BASE_DIR / "photo_uploader.log"
LOG_LEVEL = "INFO"
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
LOG_FILE_LEVEL = "INFO"  # Уровень для записи в файл
LOG_CONSOLE_LEVEL = "DEBUG"  # Уровень для вывода в консоль

INTERNAL_SHOOT_ID = "434484"
