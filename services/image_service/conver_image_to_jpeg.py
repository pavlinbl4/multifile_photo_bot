from PIL import Image
import os
from loguru import logger

from services.file_service import delete_not_jpeg


def convert_image_to_jpeg(path_to_file: str):
    supported_extensions = ['bmp', 'png', 'gif', 'tiff', 'webp', 'jpeg', 'jpg']  # Поддерживаемые расширения
    jpeg_quality = 70  # Качество JPEG, от 1 (худшее) до 95 (лучшее)

    file_ext = os.path.splitext(path_to_file)[1][1:].lower()  # Получаем расширение файла без точки
    if file_ext in supported_extensions:
        try:
            with Image.open(path_to_file) as img:
                if img.mode == 'RGBA':
                    # Преобразуем изображение в RGB, удаляя прозрачный фон
                    img = img.convert('RGB')
                path_to_jpeg_file = path_to_file.replace(file_ext, 'jpg')
                img.save(path_to_jpeg_file, 'JPEG', quality=jpeg_quality)
                logger.info("conversion successful")
                # os.remove(path_to_file)
                delete_not_jpeg(path_to_file)
                logger.info("initial file deleted")
        except Exception as e:
            logger.error(f"conversion error : {e}")
    return path_to_jpeg_file


