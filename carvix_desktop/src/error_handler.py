"""
Модуль для обработки ошибок с понятными сообщениями
"""
import traceback
from typing import Optional


class AppError(Exception):
    """Базовый класс для ошибок приложения"""
    def __init__(self, message: str, user_message: Optional[str] = None):
        self.message = message
        self.user_message = user_message or message
        super().__init__(self.message)


class DatabaseError(AppError):
    """Ошибка базы данных"""
    pass


class ValidationError(AppError):
    """Ошибка валидации данных"""
    pass


class AuthenticationError(AppError):
    """Ошибка авторизации"""
    pass


class PermissionError(AppError):
    """Ошибка прав доступа"""
    pass


class ErrorHandler:
    """Класс для обработки ошибок и логирования"""

    @staticmethod
    def handle_error(error: Exception, context: str = "") -> str:
        """
        Обработка ошибки и возврат понятного сообщения для пользователя

        Args:
            error: Исключение
            context: Контекст ошибки (где произошла)

        Returns:
            Понятное сообщение для пользователя
        """
        # Если это наша кастомная ошибка, используем пользовательское сообщение
        if isinstance(error, AppError):
            user_msg = error.user_message
            # Логируем техническое сообщение
            print(f"Error in {context}: {error.message}")
            return user_msg

        # Обработка стандартных ошибок
        error_type = type(error).__name__

        if error_type == "ConnectionError":
            user_msg = "Ошибка подключения к базе данных. Проверьте соединение с интернетом."
        elif error_type == "OperationalError":
            user_msg = "Ошибка выполнения операции в базе данных. Обратитесь к администратору."
        elif "psycopg2" in str(type(error)):
            user_msg = "Ошибка базы данных. Обратитесь к администратору."
        elif error_type == "ValueError":
            user_msg = f"Ошибка данных: {str(error)}"
        elif error_type == "KeyError":
            user_msg = "Отсутствуют необходимые данные. Обратитесь к администратору."
        elif error_type == "AttributeError":
            user_msg = "Ошибка в работе программы. Обратитесь к администратору."
        else:
            user_msg = f"Произошла ошибка: {str(error)}"

        # Логируем полную информацию об ошибке
        print(f"Error in {context}: {error_type}: {str(error)}")
        print(traceback.format_exc())

        return user_msg

    @staticmethod
    def log_error(error: Exception, context: str = ""):
        """Логирование ошибки"""
        error_type = type(error).__name__
        print(f"[ERROR] {context}: {error_type}: {str(error)}")
        print(traceback.format_exc())
