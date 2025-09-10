import asyncio
from loguru import logger

# УДАЛИТЬ импорт бота: from core import bot
from utils.shlack_uploader import web_photo_uploader

# Создаем очередь для задач Selenium
selenium_queue = asyncio.Queue()


class UploadTask:
    def __init__(self, file_path, file_name, credit, chat_id, internal_shoot_id, file_caption):
        self.file_path = file_path
        self.file_name = file_name
        self.credit = credit
        self.chat_id = chat_id
        self.internal_shoot_id = internal_shoot_id
        self.file_caption = file_caption

    def __str__(self):
        return f"Task({self.file_name}, credit={self.credit})"


async def add_upload_task(file_path, file_name, credit, chat_id, internal_shoot_id, file_caption):
    """Добавляет задачу в очередь загрузки"""
    task = UploadTask(file_path, file_name, credit, chat_id, internal_shoot_id, file_caption)
    logger.debug(f"{task.__str__()}")
    await selenium_queue.put(task)
    logger.debug(f"Added task to queue: {task}")
    return task


# Добавить аргумент bot в функцию
async def selenium_worker(bot):
    """Воркер для обработки задач Selenium"""
    logger.info("Selenium worker started")

    while True:
        try:
            # Получаем задачу из очереди
            task = await selenium_queue.get()
            logger.debug(f"Processing task: {task}")

            try:
                # Выполняем задачу
                result = await asyncio.to_thread(
                    web_photo_uploader,
                    task.file_path,
                    f'{task.file_name} \n\n{task.file_caption}',
                    task.credit,
                    task.internal_shoot_id,  # ← ДОБАВЬТЕ ЭТУ СТРОКУ
                    task.file_caption,
                )
                logger.debug(f"Task completed: {result}")

                # Использовать переданный экземпляр бота
                await bot.send_message(
                    task.chat_id,
                    f"Файл {task.file_name} обработан. Результат: {result}"
                )
            except Exception as e:
                logger.error(f"Error processing task {task}: {e}")
                await bot.send_message(
                    task.chat_id,
                    f"Ошибка при обработке файла {task.file_name}: {e}"
                )
            finally:
                # Помечаем задачу как выполненную
                selenium_queue.task_done()

        except Exception as e:
            logger.error(f"Critical error in selenium_worker: {e}")
            # Небольшая пауза перед следующей попыткой
            await asyncio.sleep(1)
