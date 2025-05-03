from pathlib import Path
from loguru import logger
from get_credentials import Credentials

# Пути к директориям
BASE_DIR = Path(__file__).parent.parent
UPLOADS_DIR = BASE_DIR / "Uploaded_images"

# Настройки бота
TOKEN = Credentials().contraption_bot
ALLOWED_USER_NAMES = {"PavlenkoEV"}

# Настройки обработки файлов
ALLOWED_FILE_TYPES = {'image/jpeg', 'image/png', 'image/x-tiff'}
MIN_CREDIT_LENGTH = 3

# Настройки логирования
LOG_FILE = BASE_DIR / "photo_uploader.log"
LOG_LEVEL = "INFO"
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"