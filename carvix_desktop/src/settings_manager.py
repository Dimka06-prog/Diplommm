"""
Модуль для управления настройками приложения
"""
from src.database import Database
from typing import Optional, Any


class SettingsManager:
    """Класс для управления настройками в базе данных"""

    @staticmethod
    def get_setting(key: str, default: Any = None) -> Any:
        """
        Получить значение настройки из базы данных

        Args:
            key: Ключ настройки
            default: Значение по умолчанию, если настройка не найдена

        Returns:
            Значение настройки или default
        """
        try:
            query = "SELECT value FROM app_settings WHERE key = %s"
            result = Database.execute_query(query, (key,))
            if result:
                return result[0]['value']
            return default
        except Exception as e:
            # Если таблица не существует или ошибка, возвращаем default
            print(f"Ошибка получения настройки {key}: {e}")
            return default

    @staticmethod
    def set_setting(key: str, value: Any) -> bool:
        """
        Установить значение настройки в базе данных

        Args:
            key: Ключ настройки
            value: Значение настройки

        Returns:
            True если успешно, False если ошибка
        """
        try:
            # Сначала проверяем, существует ли настройка
            check_query = "SELECT id FROM app_settings WHERE key = %s"
            existing = Database.execute_query(check_query, (key,))

            if existing:
                # Обновляем существующую настройку
                update_query = "UPDATE app_settings SET value = %s WHERE key = %s"
                Database.execute_query(update_query, (value, key), fetch=False)
            else:
                # Создаем новую настройку
                insert_query = "INSERT INTO app_settings (key, value) VALUES (%s, %s)"
                Database.execute_query(insert_query, (key, value), fetch=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения настройки: {e}")
            return False

    @staticmethod
    def get_all_settings() -> dict:
        """
        Получить все настройки из базы данных

        Returns:
            Словарь с настройками
        """
        try:
            query = "SELECT key, value FROM app_settings"
            results = Database.execute_query(query)
            return {row['key']: row['value'] for row in results}
        except Exception:
            return {}

    @staticmethod
    def init_default_settings():
        """Инициализация настроек по умолчанию"""
        default_settings = {
            'company_name': 'Carvix',
            'maintenance_reminder_days': '30',
            'insurance_reminder_days': '30',
            'auto_sync_gibdd': 'false',
            'session_timeout_minutes': '60',
        }

        for key, value in default_settings.items():
            SettingsManager.set_setting(key, value)


# Глобальный экземпляр менеджера настроек
settings_manager = SettingsManager()
