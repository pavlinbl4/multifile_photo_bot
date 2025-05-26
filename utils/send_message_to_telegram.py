import logging
import requests

from config.settings import TOKEN
from services.get_credentials import Credentials

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../telegram_bot.log"),  # Логирование в файл
    ]
)


def send_telegram_message(text: str):
    channel_id = Credentials().admin

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    r = requests.post(url, data={
        "chat_id": channel_id,
        "text": text
    })

    if r.status_code != 200:
        logging.error(f"post_text error: {r.status_code} - {r.text}")
        raise Exception(f"post_text error: {r.status_code} - {r.text}")

    logging.info(f"Соединение установлено,\nсообщение "
                 f"\"{text}\"  "
                 f"отправлено")


if __name__ == '__main__':
    send_telegram_message('test message')
