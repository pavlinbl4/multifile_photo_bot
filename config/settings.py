from pathlib import Path

from services.get_credentials import Credentials
from loguru import logger

# Пути к директориям
BASE_DIR = Path(__file__).parent.parent
print(f'{BASE_DIR = }')
UPLOADS_DIR = BASE_DIR / "Uploaded_images"


# Настройки бота
TOKEN = Credentials().contraption_bot
logger.info(f'Now use contraption_bot')
ALLOWED_USER_NAMES = {"PavlenkoEV"}

# Настройки обработки файлов
ALLOWED_FILE_TYPES = {'image/jpeg', 'image/png', 'image/x-tiff'}
MIN_CREDIT_LENGTH = 3

# Настройки логирования
# LOG_FILE = BASE_DIR / "photo_uploader.log"
LOG_FILE = BASE_DIR / "photo_uploader.log"
LOG_LEVEL = "INFO"
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
LOG_FILE_LEVEL = "INFO"     # Уровень для записи в файл
LOG_CONSOLE_LEVEL = "DEBUG" # Уровень для вывода в консоль
