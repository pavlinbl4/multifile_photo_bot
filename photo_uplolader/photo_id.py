import re
from loguru import logger


def extract_photo_id(current_url):
    pattern = r'KSP_\d+_\d+'
    photo_id = re.findall(pattern, current_url)[0]
    logger.info(f"Photo ID: {photo_id}")
    return photo_id



