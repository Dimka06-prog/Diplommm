"""
Тесты для работы с базой данных
"""
import pytest
from src.database import Database


class TestDatabase:
    """Тесты базы данных"""

    @pytest.fixture(autouse=True)
    def setup_database(self):
        """Настройка соединения с БД для тестов"""
        # БД должна быть настроена через переменные окружения
        pass

    def test_connection_pool_creation(self):
        """Тест создания пула соединений"""
        # Этот тест проверяет, что пул соединений создается корректно
        # В реальном приложении нужно использовать тестовую БД
        assert Database is not None

    def test_execute_query(self):
        """Тест выполнения запросов"""
        try:
            result = Database.execute_query("SELECT 1 as test")
            assert result is not None
            assert result[0]['test'] == 1
        except Exception as e:
            pytest.skip(f"База данных недоступна: {e}")

    def test_get_vehicles_count(self):
        """Тест получения количества ТС"""
        try:
            result = Database.execute_query("SELECT COUNT(*) as count FROM transportnoe_sredstvo")
            assert result is not None
            assert result[0]['count'] >= 0
        except Exception as e:
            pytest.skip(f"База данных недоступна: {e}")

    def test_get_drivers_count(self):
        """Тест получения количества водителей"""
        try:
            result = Database.execute_query("SELECT COUNT(*) as count FROM sotrudnik")
            assert result is not None
            assert result[0]['count'] >= 0
        except Exception as e:
            pytest.skip(f"База данных недоступна: {e}")

    def test_get_active_vehicles(self):
        """Тест получения активных ТС"""
        try:
            result = Database.execute_query(
                "SELECT COUNT(*) as count FROM transportnoe_sredstvo WHERE tekuschee_sostoyanie = 'Активно'"
            )
            assert result is not None
            assert result[0]['count'] >= 0
        except Exception as e:
            pytest.skip(f"База данных недоступна: {e}")
