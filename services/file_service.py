import os
from pathlib import Path
from loguru import logger
from config.settings import UPLOADS_DIR, ALLOWED_FILE_TYPES
from utils.helpers import create_dir

from services.image_service.conver_image_to_jpeg import convert_image_to_jpeg


async def save_file_to_disk(bot, file_path, destination_path):
    """Сохраняет файл, полученный от пользователя"""
    await bot.download_file(file_path, destination_path)
    logger.info(f"File saved to {destination_path}")
    return destination_path


def convert_to_jpeg_if_needed(file_path):
    """Конвертирует изображение в JPEG, если оно в другом формате"""
    if Path(file_path).suffix.lower() not in ['.jpeg', '.jpg']:
        return convert_image_to_jpeg(file_path)
    return file_path

def delete_not_jpeg(file_path):
    """delete not jpeg image file"""
    if Path(file_path).suffix.lower() not in ['.jpeg', '.jpg']:
        os.remove(file_path)


def is_valid_file(mime_type):
    """Проверяет, подходит ли тип файла для обработки"""
    return mime_type in ALLOWED_FILE_TYPES


def prepare_upload_path(file_name):
    """Подготавливает путь для загрузки файла"""
    uploads_dir = create_dir(UPLOADS_DIR)
    return Path(uploads_dir) / file_name
