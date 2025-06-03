from aiogram.types import BotCommand


def get_commands():
    """Определение команд бота"""

    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Показать справку"),
        BotCommand(command="add_image", description="Загрузить изображение"),
        BotCommand(command="cancel", description="Отменить текущую операцию"),
        BotCommand(command="finish",description="Завершить текущую загрузку"),
    ]

    return commands
