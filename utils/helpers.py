from pathlib import Path

def create_dir(dir_name):
    """Создает директорию, если она не существует"""
    directory = Path(dir_name)
    directory.mkdir(exist_ok=True, parents=True)
    return str(directory.absolute())

def is_allowed_file_type(mime_type, allowed_types):
    """Проверяет, является ли тип файла разрешенным"""
    return mime_type in allowed_types