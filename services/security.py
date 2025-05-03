from config.settings import ALLOWED_USER_NAMES

def is_user_allowed(username):
    """Проверяет, разрешен ли доступ пользователю"""
    return username in ALLOWED_USER_NAMES

def log_unauthorized_access(user):
    """Логирует попытки неавторизованного доступа"""
    with open('users.txt', 'a') as txt_user_base:
        txt_user_base.write(f'{user.full_name} - {user.id}\n')