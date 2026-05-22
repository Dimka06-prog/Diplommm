"""
Тесты для системы прав доступа (RBAC)
"""
import pytest
from src.permissions import (
    has_permission,
    get_menu_items,
    get_role_name,
    ROLE_DISPATCHER,
    ROLE_DRIVER,
    ROLE_MECHANIC,
    ROLE_ADMIN,
    PERMISSION_VIEW_DASHBOARD,
    PERMISSION_ADD_DRIVER,
    PERMISSION_MANAGE_USERS,
    PERMISSION_VIEW_OWN_SCHEDULE
)


class TestPermissions:
    """Тесты системы прав доступа"""

    def test_dispatcher_has_full_permissions(self):
        """Диспетчер должен иметь полные права на управление"""
        assert has_permission(ROLE_DISPATCHER, PERMISSION_VIEW_DASHBOARD)
        assert has_permission(ROLE_DISPATCHER, PERMISSION_ADD_DRIVER)
        assert not has_permission(ROLE_DISPATCHER, PERMISSION_MANAGE_USERS)

    def test_driver_has_limited_permissions(self):
        """Водитель должен иметь ограниченные права"""
        assert has_permission(ROLE_DRIVER, PERMISSION_VIEW_DASHBOARD)
        assert has_permission(ROLE_DRIVER, PERMISSION_VIEW_OWN_SCHEDULE)
        assert not has_permission(ROLE_DRIVER, PERMISSION_ADD_DRIVER)
        assert not has_permission(ROLE_DRIVER, PERMISSION_MANAGE_USERS)

    def test_mechanic_has_maintenance_permissions(self):
        """Механик должен иметь права на работу с ТО"""
        assert has_permission(ROLE_MECHANIC, PERMISSION_VIEW_DASHBOARD)
        assert not has_permission(ROLE_MECHANIC, PERMISSION_ADD_DRIVER)
        assert not has_permission(ROLE_MECHANIC, PERMISSION_MANAGE_USERS)

    def test_admin_has_all_permissions(self):
        """Администратор должен иметь все права"""
        assert has_permission(ROLE_ADMIN, PERMISSION_VIEW_DASHBOARD)
        assert has_permission(ROLE_ADMIN, PERMISSION_ADD_DRIVER)
        assert has_permission(ROLE_ADMIN, PERMISSION_MANAGE_USERS)

    def test_get_menu_items_by_role(self):
        """Тест получения меню для разных ролей"""
        dispatcher_menu = get_menu_items(ROLE_DISPATCHER)
        driver_menu = get_menu_items(ROLE_DRIVER)
        admin_menu = get_menu_items(ROLE_ADMIN)

        # Диспетчер должен видеть больше пунктов, чем водитель
        assert len(dispatcher_menu) > len(driver_menu)
        # Админ должен видеть больше пунктов, чем диспетчер
        assert len(admin_menu) > len(dispatcher_menu)

    def test_get_role_name(self):
        """Тест получения названия роли"""
        assert get_role_name(ROLE_DISPATCHER) == "Диспетчер"
        assert get_role_name(ROLE_DRIVER) == "Водитель"
        assert get_role_name(ROLE_MECHANIC) == "Механик"
        assert get_role_name(ROLE_ADMIN) == "Администратор"
        assert get_role_name(999) == "Неизвестно"
