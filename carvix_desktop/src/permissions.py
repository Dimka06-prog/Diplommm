"""
Система прав доступа на основе ролей (RBAC)
"""

# Роли (matching database IDs)
ROLE_ANALYST = 1
ROLE_DISPATCHER = 2
ROLE_MECHANIC = 3
ROLE_CHIEF_MECHANIC = 4
ROLE_DIRECTOR = 5
ROLE_DRIVER = 6

# Legacy role constants for compatibility
ROLE_USER = 6  # Maps to ROLE_DRIVER
ROLE_ADMIN = 5   # Maps to ROLE_DIRECTOR

ROLE_NAMES = {
    ROLE_ANALYST: "Аналитик",
    ROLE_DISPATCHER: "Диспетчер",
    ROLE_MECHANIC: "Механик",
    ROLE_CHIEF_MECHANIC: "Главный механик",
    ROLE_DIRECTOR: "Директор",
    ROLE_DRIVER: "Водитель",
    # Legacy mappings
    ROLE_USER: "Водитель",
    ROLE_ADMIN: "Администратор"
}

# Права доступа
PERMISSION_VIEW_DASHBOARD = "view_dashboard"
PERMISSION_VIEW_DRIVERS = "view_drivers"
PERMISSION_ADD_DRIVER = "add_driver"
PERMISSION_EDIT_DRIVER = "edit_driver"
PERMISSION_DELETE_DRIVER = "delete_driver"
PERMISSION_VIEW_VEHICLES = "view_vehicles"
PERMISSION_ADD_VEHICLE = "add_vehicle"
PERMISSION_EDIT_VEHICLE = "edit_vehicle"
PERMISSION_DELETE_VEHICLE = "delete_vehicle"
PERMISSION_VIEW_SCHEDULE = "view_schedule"
PERMISSION_ADD_SCHEDULE = "add_schedule"
PERMISSION_EDIT_SCHEDULE = "edit_schedule"
PERMISSION_DELETE_SCHEDULE = "delete_schedule"
PERMISSION_VIEW_OWN_SCHEDULE = "view_own_schedule"
PERMISSION_VIEW_MAINTENANCE = "view_maintenance"
PERMISSION_ADD_MAINTENANCE = "add_maintenance"
PERMISSION_EDIT_MAINTENANCE = "edit_maintenance"
PERMISSION_DELETE_MAINTENANCE = "delete_maintenance"
PERMISSION_VIEW_FINES = "view_fines"
PERMISSION_ADD_FINE = "add_fine"
PERMISSION_EDIT_FINE = "edit_fine"
PERMISSION_DELETE_FINE = "delete_fine"
PERMISSION_VIEW_OWN_FINES = "view_own_fines"
PERMISSION_VIEW_REPORTS = "view_reports"
PERMISSION_VIEW_PROFILE = "view_profile"
# Admin-specific permissions
PERMISSION_MANAGE_USERS = "manage_users"
PERMISSION_MANAGE_ROLES = "manage_roles"
PERMISSION_SYSTEM_SETTINGS = "system_settings"
PERMISSION_ADVANCED_REPORTS = "advanced_reports"

# Права для каждой роли
ROLE_PERMISSIONS = {
    ROLE_ANALYST: [
        PERMISSION_VIEW_DASHBOARD,
        PERMISSION_VIEW_REPORTS,
        PERMISSION_VIEW_PROFILE,
    ],
    ROLE_DISPATCHER: [
        PERMISSION_VIEW_DASHBOARD,
        PERMISSION_VIEW_DRIVERS,
        PERMISSION_ADD_DRIVER,
        PERMISSION_EDIT_DRIVER,
        PERMISSION_DELETE_DRIVER,
        PERMISSION_VIEW_VEHICLES,
        PERMISSION_ADD_VEHICLE,
        PERMISSION_EDIT_VEHICLE,
        PERMISSION_DELETE_VEHICLE,
        PERMISSION_VIEW_SCHEDULE,
        PERMISSION_ADD_SCHEDULE,
        PERMISSION_EDIT_SCHEDULE,
        PERMISSION_DELETE_SCHEDULE,
        PERMISSION_VIEW_MAINTENANCE,
        PERMISSION_ADD_MAINTENANCE,
        PERMISSION_EDIT_MAINTENANCE,
        PERMISSION_DELETE_MAINTENANCE,
        PERMISSION_VIEW_FINES,
        PERMISSION_ADD_FINE,
        PERMISSION_EDIT_FINE,
        PERMISSION_DELETE_FINE,
        PERMISSION_VIEW_REPORTS,
        PERMISSION_VIEW_PROFILE,
    ],
    ROLE_MECHANIC: [
        PERMISSION_VIEW_DASHBOARD,
        PERMISSION_VIEW_VEHICLES,
        PERMISSION_VIEW_MAINTENANCE,
        PERMISSION_ADD_MAINTENANCE,
        PERMISSION_EDIT_MAINTENANCE,
        PERMISSION_DELETE_MAINTENANCE,
        PERMISSION_VIEW_PROFILE,
    ],
    ROLE_CHIEF_MECHANIC: [
        PERMISSION_VIEW_DASHBOARD,
        PERMISSION_VIEW_VEHICLES,
        PERMISSION_VIEW_MAINTENANCE,
        PERMISSION_ADD_MAINTENANCE,
        PERMISSION_EDIT_MAINTENANCE,
        PERMISSION_DELETE_MAINTENANCE,
        PERMISSION_VIEW_REPORTS,
        PERMISSION_VIEW_PROFILE,
    ],
    ROLE_DIRECTOR: [
        PERMISSION_VIEW_DASHBOARD,
        PERMISSION_VIEW_DRIVERS,
        PERMISSION_ADD_DRIVER,
        PERMISSION_EDIT_DRIVER,
        PERMISSION_DELETE_DRIVER,
        PERMISSION_VIEW_VEHICLES,
        PERMISSION_ADD_VEHICLE,
        PERMISSION_EDIT_VEHICLE,
        PERMISSION_DELETE_VEHICLE,
        PERMISSION_VIEW_SCHEDULE,
        PERMISSION_ADD_SCHEDULE,
        PERMISSION_EDIT_SCHEDULE,
        PERMISSION_DELETE_SCHEDULE,
        PERMISSION_VIEW_MAINTENANCE,
        PERMISSION_ADD_MAINTENANCE,
        PERMISSION_EDIT_MAINTENANCE,
        PERMISSION_DELETE_MAINTENANCE,
        PERMISSION_VIEW_FINES,
        PERMISSION_ADD_FINE,
        PERMISSION_EDIT_FINE,
        PERMISSION_DELETE_FINE,
        PERMISSION_VIEW_REPORTS,
        PERMISSION_VIEW_PROFILE,
        PERMISSION_MANAGE_USERS,
        PERMISSION_MANAGE_ROLES,
        PERMISSION_SYSTEM_SETTINGS,
        PERMISSION_ADVANCED_REPORTS,
    ],
    ROLE_DRIVER: [
        PERMISSION_VIEW_DASHBOARD,
        PERMISSION_VIEW_OWN_SCHEDULE,
        PERMISSION_VIEW_OWN_FINES,
        PERMISSION_VIEW_PROFILE,
    ],
    # Legacy mappings
    ROLE_USER: [
        PERMISSION_VIEW_DASHBOARD,
        PERMISSION_VIEW_OWN_SCHEDULE,
        PERMISSION_VIEW_OWN_FINES,
        PERMISSION_VIEW_PROFILE,
    ],
    ROLE_ADMIN: [
        PERMISSION_VIEW_DASHBOARD,
        PERMISSION_VIEW_DRIVERS,
        PERMISSION_ADD_DRIVER,
        PERMISSION_EDIT_DRIVER,
        PERMISSION_DELETE_DRIVER,
        PERMISSION_VIEW_VEHICLES,
        PERMISSION_ADD_VEHICLE,
        PERMISSION_EDIT_VEHICLE,
        PERMISSION_DELETE_VEHICLE,
        PERMISSION_VIEW_SCHEDULE,
        PERMISSION_ADD_SCHEDULE,
        PERMISSION_EDIT_SCHEDULE,
        PERMISSION_DELETE_SCHEDULE,
        PERMISSION_VIEW_MAINTENANCE,
        PERMISSION_ADD_MAINTENANCE,
        PERMISSION_EDIT_MAINTENANCE,
        PERMISSION_DELETE_MAINTENANCE,
        PERMISSION_VIEW_FINES,
        PERMISSION_ADD_FINE,
        PERMISSION_EDIT_FINE,
        PERMISSION_DELETE_FINE,
        PERMISSION_VIEW_REPORTS,
        PERMISSION_VIEW_PROFILE,
        PERMISSION_MANAGE_USERS,
        PERMISSION_MANAGE_ROLES,
        PERMISSION_SYSTEM_SETTINGS,
        PERMISSION_ADVANCED_REPORTS,
    ],
}

# Меню для каждой роли
ROLE_MENU_ITEMS = {
    ROLE_ANALYST: [
        ("dashboard", "Дашборд", "📊"),
        ("reports", "Отчеты", "📈"),
        ("profile", "Профиль", "👤"),
    ],
    ROLE_DISPATCHER: [
        ("dashboard", "Дашборд", "📊"),
        ("drivers", "Водители", "👤"),
        ("vehicles", "Транспорт", "🚗"),
        ("schedule", "График", "📅"),
        ("maintenance", "ТО и Страховка", "🔧"),
        ("fines", "Штрафы", "📋"),
        ("reports", "Отчеты", "📈"),
    ],
    ROLE_MECHANIC: [
        ("dashboard", "Дашборд", "📊"),
        ("vehicles", "Транспорт", "�"),
        ("maintenance", "ТО и Ремонт", "�"),
        ("profile", "Профиль", "👤"),
    ],
    ROLE_CHIEF_MECHANIC: [
        ("dashboard", "Дашборд", "📊"),
        ("vehicles", "Транспорт", "🚗"),
        ("maintenance", "ТО и Ремонт", "🔧"),
        ("reports", "Отчеты", "📈"),
        ("profile", "Профиль", "👤"),
    ],
    ROLE_DIRECTOR: [
        ("dashboard", "Дашборд", "📊"),
        ("drivers", "Водители", "👤"),
        ("vehicles", "Транспорт", "🚗"),
        ("schedule", "График", "📅"),
        ("maintenance", "ТО и Страховка", "🔧"),
        ("fines", "Штрафы", "📋"),
        ("reports", "Отчеты", "📈"),
        ("users", "Пользователи", "👥"),
        ("settings", "Настройки", "⚙️"),
    ],
    ROLE_DRIVER: [
        ("dashboard", "Дашборд", "📊"),
        ("schedule", "Мой график", "📅"),
        ("fines", "Мои штрафы", "📋"),
        ("profile", "Профиль", "👤"),
    ],
    # Legacy mappings
    ROLE_USER: [
        ("dashboard", "Дашборд", "📊"),
        ("schedule", "Мой график", "📅"),
        ("fines", "Мои штрафы", "📋"),
        ("profile", "Профиль", "👤"),
    ],
    ROLE_ADMIN: [
        ("dashboard", "Дашборд", "📊"),
        ("drivers", "Водители", "👤"),
        ("vehicles", "Транспорт", "🚗"),
        ("schedule", "График", "📅"),
        ("maintenance", "ТО и Страховка", "🔧"),
        ("fines", "Штрафы", "📋"),
        ("reports", "Отчеты", "📈"),
        ("users", "Пользователи", "👥"),
        ("settings", "Настройки", "⚙️"),
    ],
}

def has_permission(role_id: int, permission: str) -> bool:
    """Проверяет, имеет ли роль указанное разрешение"""
    return permission in ROLE_PERMISSIONS.get(role_id, [])

def get_menu_items(role_id: int):
    """Возвращает список пунктов меню для роли"""
    return ROLE_MENU_ITEMS.get(role_id, ROLE_MENU_ITEMS[ROLE_DRIVER])

def get_role_name(role_id: int) -> str:
    """Возвращает название роли"""
    return ROLE_NAMES.get(role_id, "Неизвестно")
