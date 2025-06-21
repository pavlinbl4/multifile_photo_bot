import re
from loguru import logger

logger.add("../photo_uploader.log", format="{time} {level} {message}", level="DEBUG")


def extract_photo_id(current_url):
    pattern = r'KSP_\d+_\d+'
    photo_id = re.findall(pattern, current_url)[0]
    logger.debug(f"Photo ID: {photo_id}")
    return photo_id
