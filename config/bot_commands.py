from aiogram.types import BotCommand

# При необходимости можно определить новые команды
COMMANDS = [
    BotCommand(command="start", description="Запустить бота"),
    BotCommand(command="help", description="Показать справку"),
    BotCommand(command="add_image", description="Загрузить изображение"),
    BotCommand(command="cancel", description="Отменить текущую операцию")
]
