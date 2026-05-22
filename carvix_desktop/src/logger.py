"""
Модуль для логирования действий и ошибок
"""
import logging
import os
from datetime import datetime
from typing import Optional


class AppLogger:
    """Класс для логирования действий в приложении"""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self._setup_logger()

    def _setup_logger(self):
        """Настройка логгера"""
        # Создаем директорию для логов, если она не существует
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Настраиваем логгер
        self.logger = logging.getLogger("CarvixDesktop")
        self.logger.setLevel(logging.INFO)

        # Формат логов
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Файловый хендлер
        log_file = os.path.join(self.log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # Консольный хендлер
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # Добавляем хендлеры
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log_login(self, user_id: int, username: str, role: str, success: bool):
        """Логирование входа в систему"""
        if success:
            self.logger.info(f"LOGIN SUCCESS - User ID: {user_id}, Username: {username}, Role: {role}")
        else:
            self.logger.warning(f"LOGIN FAILED - Username: {username}")

    def log_logout(self, user_id: int, username: str):
        """Логирование выхода из системы"""
        self.logger.info(f"LOGOUT - User ID: {user_id}, Username: {username}")

    def log_action(self, user_id: int, action: str, details: Optional[str] = None):
        """Логирование действия пользователя"""
        message = f"ACTION - User ID: {user_id}, Action: {action}"
        if details:
            message += f", Details: {details}"
        self.logger.info(message)

    def log_error(self, user_id: Optional[int], error: str, context: Optional[str] = None):
        """Логирование ошибки"""
        message = f"ERROR - User ID: {user_id}, Error: {error}"
        if context:
            message += f", Context: {context}"
        self.logger.error(message)

    def log_database_query(self, query: str, params: Optional[tuple] = None):
        """Логирование запроса к БД (для отладки)"""
        message = f"DB QUERY - Query: {query[:100]}..."
        if params:
            message += f", Params: {params}"
        self.logger.debug(message)


# Глобальный экземпляр логгера
logger = AppLogger()
