"""
this function upload image to archive via web uploader
"""

import os
import time
from typing import Tuple
from loguru import logger
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# from config.settings import INTERNAL_SHOOT_ID, BASE_UPLOAD_LINK
from config.settings import BASE_UPLOAD_LINK
from services.authorization import AuthorizationHandler
from utils.photo_id import extract_photo_id


def find_element(driver, selector: Tuple[str, str], timeout: int = 5):
    """Wait for an element to be clickable and return it."""
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(selector))


def upload_file(driver, path_to_file: str, upload_button_selector: Tuple[str, str]):
    """Upload a file to the web form."""
    upload_button = find_element(driver, upload_button_selector)
    if os.path.exists(path_to_file):
        upload_button.send_keys(path_to_file)
    else:
        raise FileNotFoundError(f"File not found: {path_to_file}")


def fill_field(driver, field_selector: Tuple[str, str], text: str):
    """Fill an input field with specified text."""
    field = find_element(driver, field_selector)
    field.clear()
    field.send_keys(text)


def web_photo_uploader(
        path_to_file: str,
        image_caption: str,
        author: str,
        internal_shoot_id: str
):
    """Upload a photo to the web archive."""
    try:
        driver = AuthorizationHandler().authorize()
        driver.implicitly_wait(20)
        logger.debug(f'{driver.title = }')
        if driver.title != 'Фотоархив ИД "Коммерсантъ" | Поиск':
            logger.error("Authorization failed")
            return "Authorization failed"

        logger.info("Authorization successful")
        upload_link = f'{BASE_UPLOAD_LINK}{internal_shoot_id}'
        driver.get(upload_link)

        logger.info(f"Page title: {driver.title}")
        logger.info(find_element(driver, (By.XPATH, '//*[@id="HeaderText"]')).text)

    except TimeoutException as e:
        logger.error(f"Timeout occurred: {e}")
        return f"Timeout occurred: {e}"
    except Exception as ex:
        logger.error(f"selenium unexpected error occurred: {ex}")
        return f"selenium unexpected error occurred: {ex}"

    try:
        upload_file(driver, path_to_file, (By.XPATH, "//input[@id='InputFile']"))
        find_element(driver, (By.XPATH, "//input[@type='submit']")).click()
    except Exception as ex:
        logger.error(f"Selenium error occurred: {ex}")
        return f"Selenium error occurred: {ex}"
    try:
        description_field_selector = (By.XPATH, '//textarea[@name="DescriptionControl$Description"]')
        fill_field(driver, description_field_selector, image_caption)

        author_field_selector = (By.XPATH, '//input[@name="DescriptionControl$NewPseudonym"]')
        fill_field(driver, author_field_selector, author)

        current_url = driver.current_url
        logger.info(f"Uploaded photo URL: {current_url}")
        photo_id = extract_photo_id(current_url)
        logger.info(f"Photo ID: {photo_id}")

        # find upload photo button and click it
        add_photo_button_selector = (By.XPATH, '//input[@name="AddPhotoButton"]')
        find_element(driver, add_photo_button_selector).click()

        wait_for_load = (By.XPATH, "//span[@id='RecentyAddedHeader']")
        find_element(driver, wait_for_load)
        time.sleep(2)




    except FileNotFoundError as fnf_error:
        logger.error(f"Element not found: {fnf_error}")
        return f"Element not found: {fnf_error}"
    except NoSuchElementException as no_elem:
        logger.error(f"Element not found: {no_elem}")
        return f"Element not found: {no_elem}"
    except Exception as ex:
        logger.error(f"Selenium error occurred during file upload: {ex}")
        return f"Selenium error occurred during file upload: {ex}"

    finally:

        if os.path.exists(path_to_file):
            os.remove(path_to_file)
        driver.quit()

    return photo_id
