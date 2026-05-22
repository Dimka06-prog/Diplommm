# Carvix Desktop — Система учета водителей и транспортных средств

Десктопное приложение для автоматизации базы водителей и автомобилей с историей техосмотров, штрафов и графиков работы. Работает с единой базой данных PostgreSQL веб-проекта Carvix.

## 📋 Оглавление

- [Обзор проекта](#обзор-проекта)
- [Архитектура](#архитектура)
- [База данных](#база-данных)
- [Ролевая модель доступа (RBAC)](#ролевая-модель-доступа-rbac)
- [Диаграммы](#диаграммы)
- [Установка](#установка)
- [Структура проекта](#структура-проекта)
- [Дизайн](#дизайн)
- [Тестирование](#тестирование)

## Обзор проекта

Carvix Desktop — это комплексное десктопное приложение для управления автопарком, разработанное на Python с использованием PyQt6. Приложение обеспечивает:

- **Управление персоналом**: Учет водителей, механиков и диспетчеров с ролевым доступом
- **Управление парком**: Полный учет транспортных средств с VIN, пробегом, состоянием
- **Планирование смен**: Распределение водителей по ТС и графикам работы
- **Мониторинг ТО**: Отслеживание сроков технического обслуживания и страхования
- **Учет штрафов**: Интеграция с ГИБДД API для проверки штрафов
- **Аналитика**: Графики и отчеты для принятия решений
- **Безопасность**: Хеширование паролей, логирование действий, тайм-аут сессии

### Ключевые особенности

- **Единая БД**: Использует ту же базу данных, что и веб-версия Carvix
- **RBAC**: 4 роли с разными правами доступа (Диспетчер, Водитель, Механик, Администратор)
- **Валидация данных**: Проверка корректности ввода (ФИО, логин, пароль, VIN, гос. номер)
- **Логирование**: Запись всех действий пользователей для аудита
- **Настройки**: Хранение настроек приложения в базе данных
- **Визуализация**: Графики и диаграммы для анализа данных

## Архитектура

### Компонентная архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                        Carvix Desktop                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │ Auth Dialog  │───▶│ Main Window  │───▶│  Pages       │    │
│  │ (Вход/Роль)  │    │ (Sidebar+Nav)│    │  (CRUD)      │    │
│  └──────────────┘    └──────────────┘    └──────────────┘    │
│                              │                   │            │
│                              ▼                   ▼            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │   Logger     │    │   Settings   │    │  Validator   │    │
│  │ (Аудит)      │    │  Manager     │    │  (Валидация) │    │
│  └──────────────┘    └──────────────┘    └──────────────┘    │
│                              │                   │            │
│                              └───────────┬───────┘            │
│                                          ▼                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Database Layer (PostgreSQL)              │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │  Pool    │  │  Query   │  │  Models  │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Поток данных (Data Flow)

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │────▶│  UI Page │────▶│ Validator│────▶│ Database │
│ (Действие)│     │  (Form)  │     │  (Check) │     │ (Save)   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                 │                 │                 │
     │                 ▼                 ▼                 │
     │            ┌──────────┐     ┌──────────┐             │
     └────────────│  Logger  │────▶│  Error   │─────────────┘
                  │ (Audit)  │     │ Handler │
                  └──────────┘     └──────────┘
```

## База данных

### ER-диаграмма (Entity-Relationship)

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  rol        │       │sotrudnik    │       │podrazdelenie│
│─────────────│       │─────────────│       │─────────────│
│ id (PK)     │◀──────│ rol_id (FK) │       │ id (PK)     │
│ nazvanie    │       │ id (PK)     │───────▶│ nazvanie    │
└─────────────┘       │ fio         │       └─────────────┘
                      │ login       │
                      │ parol_hash │
                      │ license_num │
                      │ phone       │
                      │ podraz_id   │
                      └─────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  marka      │       │transportnoe │       │  model      │
│─────────────│       │_sredstvo    │       │─────────────│
│ id (PK)     │◀──────│ model_id(FK)│───────▶│ id (PK)     │
│ nazvanie    │       │ id (PK)     │       │ nazvanie    │
└─────────────┘       │ gos_nomer   │       │ marka_id(FK)│
                      │ invent_nomer│       └─────────────┘
                      │ vin         │
                      │ probeg      │
                      │ tekuschee_  │
                      │  sostoyanie │
                      │ to_expiry   │
                      │ insurance_  │
                      │  expiry     │
                      │ podraz_id   │
                      │ assigned_   │
                      │  driver_id  │
                      └─────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│ fines       │       │work_schedule│       │ maintenance │
│─────────────│       │─────────────│       │─────────────│
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ ts_id (FK)  │◀──────│ ts_id (FK)  │       │ ts_id (FK)  │◀───
│ date        │       │ driver_id   │       │ date        │
│ amount      │       │ date        │       │ type        │
│ description│       │ shift_start │       │ description │
│ status      │       │ shift_end   │       │ status      │
└─────────────┘       └─────────────┘       └─────────────┘
```

### Таблицы базы данных

#### 1. **rol** (Роли пользователей)
```sql
CREATE TABLE rol (
    id SERIAL PRIMARY KEY,
    nazvanie VARCHAR(50) NOT NULL  -- Диспетчер, Водитель, Механик, Администратор
);
```

#### 2. **podrazdelenie** (Подразделения)
```sql
CREATE TABLE podrazdelenie (
    id SERIAL PRIMARY KEY,
    nazvanie VARCHAR(100) NOT NULL
);
```

#### 3. **sotrudnik** (Сотрудники/Водители)
```sql
CREATE TABLE sotrudnik (
    id SERIAL PRIMARY KEY,
    fio VARCHAR(255) NOT NULL,
    login VARCHAR(50) UNIQUE NOT NULL,
    parol_hash VARCHAR(255) NOT NULL,
    license_number VARCHAR(20),
    phone VARCHAR(20),
    rol_id INTEGER REFERENCES rol(id),
    podrazdelenie_id INTEGER REFERENCES podrazdelenie(id)
);
```

#### 4. **marka** (Марки автомобилей)
```sql
CREATE TABLE marka (
    id SERIAL PRIMARY KEY,
    nazvanie VARCHAR(100) NOT NULL
);
```

#### 5. **model** (Модели автомобилей)
```sql
CREATE TABLE model (
    id SERIAL PRIMARY KEY,
    nazvanie VARCHAR(100) NOT NULL,
    marka_id INTEGER REFERENCES marka(id)
);
```

#### 6. **transportnoe_sredstvo** (Транспортные средства)
```sql
CREATE TABLE transportnoe_sredstvo (
    id SERIAL PRIMARY KEY,
    gos_nomer VARCHAR(20) UNIQUE NOT NULL,
    invent_nomer VARCHAR(20) UNIQUE NOT NULL,
    vin VARCHAR(17) UNIQUE NOT NULL,
    probeg INTEGER DEFAULT 0,
    model_id INTEGER REFERENCES model(id),
    tekuschee_sostoyanie VARCHAR(50) DEFAULT 'Активно',
    to_expiry DATE,
    insurance_expiry DATE,
    podrazdelenie_id INTEGER REFERENCES podrazdelenie(id),
    assigned_driver_id INTEGER REFERENCES sotrudnik(id)
);
```

#### 7. **work_schedule** (График работы)
```sql
CREATE TABLE work_schedule (
    id SERIAL PRIMARY KEY,
    ts_id INTEGER REFERENCES transportnoe_sredstvo(id),
    driver_id INTEGER REFERENCES sotrudnik(id),
    date DATE NOT NULL,
    shift_start TIME,
    shift_end TIME
);
```

#### 8. **fines** (Штрафы)
```sql
CREATE TABLE fines (
    id SERIAL PRIMARY KEY,
    ts_id INTEGER REFERENCES transportnoe_sredstvo(id),
    date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'Не оплачен'
);
```

#### 9. **maintenance** (ТО и Страховка)
```sql
CREATE TABLE maintenance (
    id SERIAL PRIMARY KEY,
    ts_id INTEGER REFERENCES transportnoe_sredstvo(id),
    date DATE NOT NULL,
    type VARCHAR(50) NOT NULL,  -- ТО или Страховка
    description TEXT,
    status VARCHAR(50) DEFAULT 'Запланировано'
);
```

#### 10. **app_settings** (Настройки приложения)
```sql
CREATE TABLE app_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Ролевая модель доступа (RBAC)

### Матрица прав доступа

| Действие | Диспетчер | Водитель | Механик | Администратор |
|----------|-----------|----------|---------|--------------|
| **Водители** |
| Просмотр списка | ✅ | ✅ (себя) | ✅ | ✅ |
| Добавление | ✅ | ❌ | ❌ | ✅ |
| Редактирование | ✅ | ❌ | ❌ | ✅ |
| Удаление | ✅ | ❌ | ❌ | ✅ |
| **Транспортные средства** |
| Просмотр списка | ✅ | ✅ (свои) | ✅ | ✅ |
| Добавление | ✅ | ❌ | ❌ | ✅ |
| Редактирование | ✅ | ❌ | ❌ | ✅ |
| Удаление | ✅ | ❌ | ❌ | ✅ |
| **График работы** |
| Просмотр | ✅ | ✅ (себя) | ✅ | ✅ |
| Добавление | ✅ | ❌ | ❌ | ✅ |
| Редактирование | ✅ | ❌ | ❌ | ✅ |
| Удаление | ✅ | ❌ | ❌ | ✅ |
| **Штрафы** |
| Просмотр | ✅ | ✅ (свои) | ✅ | ✅ |
| Добавление | ✅ | ❌ | ❌ | ✅ |
| Редактирование | ✅ | ❌ | ❌ | ✅ |
| Удаление | ✅ | ❌ | ❌ | ✅ |
| **ТО и Страховка** |
| Просмотр | ✅ | ✅ | ✅ | ✅ |
| Добавление | ✅ | ❌ | ✅ | ✅ |
| Редактирование | ✅ | ❌ | ✅ | ✅ |
| Удаление | ✅ | ❌ | ✅ | ✅ |
| **Администрирование** |
| Управление пользователями | ❌ | ❌ | ❌ | ✅ |
| Управление ролями | ❌ | ❌ | ❌ | ✅ |
| Системные настройки | ❌ | ❌ | ❌ | ✅ |
| Расширенные отчеты | ✅ | ❌ | ❌ | ✅ |

### Права доступа (Permissions)

```python
# Общие права
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

PERMISSION_VIEW_FINES = "view_fines"
PERMISSION_ADD_FINE = "add_fine"
PERMISSION_EDIT_FINE = "edit_fine"
PERMISSION_DELETE_FINE = "delete_fine"

PERMISSION_VIEW_MAINTENANCE = "view_maintenance"
PERMISSION_ADD_MAINTENANCE = "add_maintenance"
PERMISSION_EDIT_MAINTENANCE = "edit_maintenance"
PERMISSION_DELETE_MAINTENANCE = "delete_maintenance"

# Админ права
PERMISSION_MANAGE_USERS = "manage_users"
PERMISSION_MANAGE_ROLES = "manage_roles"
PERMISSION_SYSTEM_SETTINGS = "system_settings"
PERMISSION_ADVANCED_REPORTS = "advanced_reports"
```

## Диаграммы

### 1. Диаграмма классов (Class Diagram)

```
┌─────────────────────────────────────────────────────────────────┐
│                         Presentation Layer                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │ AuthDialog   │    │ MainWindow   │    │  BasePage    │    │
│  │──────────────│    │──────────────│    │──────────────│    │
│  │ - login_input│    │ - user_data  │    │ - user_data  │    │
│  │ - pass_input │    │ - pages      │    │ - init_ui()   │    │
│  │ - role_combo │    │ - sidebar    │    │ - refresh_    │    │
│  │              │    │              │    │   data()      │    │
│  │ + authenti-  │    │ + create_    │    │              │    │
│  │   cate()     │    │   sidebar()  │    └──────────────┘    │
│  └──────────────┘    │ + navigate() │           │            │
│                      │ + logout()   │           │            │
│                      └──────────────┘           ▼            │
│                              │           ┌──────────────┐    │
│                              │           │ DashboardPage│    │
│                              │           │ DriversPage  │    │
│                              │           │ VehiclesPage │    │
│                              │           │ SchedulePage │    │
│                              │           │ FinesPage    │    │
│                              │           │ MaintenancePg│    │
│                              │           │ ReportsPage  │    │
│                              │           │ UsersPage    │    │
│                              │           │ SettingsPage │    │
│                              │           └──────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Business Layer                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │ Validator    │    │ ErrorHandler │    │  Logger      │    │
│  │──────────────│    │──────────────│    │──────────────│    │
│  │ + validate_  │    │ + handle_    │    │ + log_login()│    │
│  │   fio()      │    │   error()    │    │ + log_logout()│    │
│  │ + validate_  │    │ + log_error()│    │ + log_action()│    │
│  │   login()    │    │              │    │ + log_error()│    │
│  │ + validate_  │    └──────────────┘    └──────────────┘    │
│  │   password() │                                                 │
│  │ + validate_  │                                                 │
│  │   gos_nomer()│                                                 │
│  └──────────────┘                                                 │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐                           │
│  │SettingsMgr   │    │ Permissions  │                           │
│  │──────────────│    │──────────────│                           │
│  │ + get_       │    │ + has_       │                           │
│  │   setting()  │    │   permission()│                           │
│  │ + set_       │    │ + get_menu_  │                           │
│  │   setting()  │    │   items()    │                           │
│  └──────────────┘    └──────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Data Layer                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │  Database    │    │ Connection   │    │   Models     │    │
│  │──────────────│    │   Pool       │    │──────────────│    │
│  │ + execute_   │    │──────────────│    │ - Employee   │    │
│  │   query()    │    │ - pool       │    │ - Vehicle    │    │
│  │ + close_all()│    │ - get_conn() │    │ - Fine       │    │
│  └──────────────┘    └──────────────┘    │ - Schedule   │    │
│                                           │ - Maintenance│    │
│                                           └──────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Диаграмма последовательности (Sequence Diagram) - Авторизация

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐
│  User    │     │ AuthDialog   │     │  Database    │     │  Logger   │
└──────────┘     └──────────────┘     └──────────────┘     └──────────┘
    │                  │                     │                     │
    │ Ввод логина/    │                     │                     │
    │ пароля          │                     │                     │
    │─────────────────▶│                     │                     │
    │                  │                     │                     │
    │                  │ authenticate()      │                     │
    │                  │─────────────────────▶│                     │
    │                  │ SELECT * FROM       │                     │
    │                  │ sotrudnik WHERE     │                     │
    │                  │ login = ?           │                     │
    │                  │                     │                     │
    │                  │                     │ Возвращает данные   │
    │                  │                     │ пользователя       │
    │                  │◀────────────────────│                     │
    │                  │                     │                     │
    │                  │ Проверка пароля     │                     │
    │                  │ (bcrypt)            │                     │
    │                  │                     │                     │
    │                  │ log_login()         │                     │
    │                  │─────────────────────────────────────────▶│
    │                  │                     │                     │
    │                  │ authenticated.emit()│                     │
    │                  │─────────────────────▶│                     │
    │                  │                     │                     │
    │                  │ accept()            │                     │
    │◀─────────────────│                     │                     │
```

### 3. Диаграмма состояния (State Diagram) - Сессия пользователя

```
┌────────────┐
│   Start    │
└─────┬──────┘
      │
      ▼
┌────────────┐
│ Authenti-  │
│ cated      │
└─────┬──────┘
      │
      ▼
┌────────────┐     Тайм-аут     ┌────────────┐
│   Active   │─────────────────▶│  Timeout   │
│   Session  │                 └─────┬──────┘
└─────┬──────┘                       │
      │                              ▼
      │                         ┌────────────┐
      │                         │   Logout    │
      │                         └─────┬──────┘
      │                               │
      │         Logout               │
      └───────────────────────────────┘
```

### 4. Диаграмма развертывания (Deployment Diagram)

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Workstation                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Carvix Desktop Application                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │   UI      │  │  Logic   │  │  Models  │           │   │
│  │  │ (PyQt6)   │  │ (Python) │  │          │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  │                                                           │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │         Database Connection Pool              │   │   │
│  │  │              (psycopg2-binary)                 │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ SSL/TLS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PostgreSQL Database Server                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Carvix Database                             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │ sotrudnik│  │transport │  │  fines   │           │   │
│  │  └──────────┘  │_sredstvo│  └──────────┘           │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │  rol     │  │schedule │  │mainten.  │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  │                                                           │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │              Connection Pool                     │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 5. Диаграмма использования (Use Case Diagram)

```
┌─────────────────────────────────────────────────────────────────┐
│                         Carvix Desktop                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐                                               │
│  │   Диспетчер   │                                               │
│  └──────┬───────┘                                               │
│         │                                                       │
│         ├───▶ Управление водителями                              │
│         ├───▶ Управление ТС                                      │
│         ├───▶ Управление графиком работы                        │
│         ├───▶ Управление штрафами                                │
│         ├───▶ Просмотр ТО                                       │
│         └───▶ Генерация отчетов                                 │
│                                                                 │
│  ┌──────────────┐                                               │
│  │   Водитель   │                                               │
│  └──────┬───────┘                                               │
│         │                                                       │
│         ├───▶ Просмотр своего профиля                          │
│         ├───▶ Просмотр своего графика                           │
│         ├───▶ Просмотр своих штрафов                            │
│         └───▶ Смена пароля                                      │
│                                                                 │
│  ┌──────────────┐                                               │
│  │   Механик    │                                               │
│  └──────┬───────┘                                               │
│         │                                                       │
│         ├───▶ Просмотр ТС                                       │
│         ├───▶ Управление ТО                                     │
│         └───▶ Управление ремонтами                              │
│                                                                 │
│  ┌──────────────┐                                               │
│  │ Администратор │                                               │
│  └──────┬───────┘                                               │
│         │                                                       │
│         ├───▶ Все права диспетчера                             │
│         ├───▶ Управление пользователями                         │
│         ├───▶ Управление ролями                                 │
│         └───▶ Системные настройки                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Возможности

- **Учет водителей**: Полный CRUD (создание, чтение, редактирование, удаление) водителей с ФИО, лицензией, телефоном, ролью доступа
- **Учет ТС**: Полный CRUD (создание, чтение, редактирование, удаление) транспортных средств с маркой, VIN, пробегом, состоянием, привязкой водителя
- **График работы**: Полный CRUD (создание, чтение, редактирование, удаление) распределения смен водителей и ТС
- **ТО и Страховка**: Мониторинг сроков техосмотров и страхования, система напоминаний
- **Штрафы**: Полный CRUD (создание, чтение, редактирование, удаление) штрафов с интеграцией ГИБДД API
- **Отчеты**: Пробег по ТС, штрафы за период, ТО по водителям с визуализацией в виде графиков
- **Роли доступа**: Диспетчер, Водитель, Механик, Администратор с разными правами доступа
- **Валидация данных**: Проверка корректности ввода (ФИО, логин, пароль, VIN, гос. номер)
- **Логирование**: Запись всех действий пользователей для аудита
- **Настройки**: Хранение настроек приложения в базе данных
- **Тайм-аут сессии**: Автоматический выход при бездействии

## Установка

### Требования
- Python 3.8+
- PostgreSQL 12+
- PyQt6
- matplotlib

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Настройка базы данных

**Вариант 1: Облачная БД (рекомендуется для разработки)**
1. Создайте бесплатную БД на [Neon](https://neon.tech), [Supabase](https://supabase.com) или [Railway](https://railway.app)
2. Скопируйте строку подключения (DATABASE_URL)
3. Настройте подключение в файле `.env`:
```
DATABASE_URL=postgresql://username:password@host/database?sslmode=require
```
4. Выполните миграции через SQL Editor в интерфейсе облачной БД или:
```bash
psql "DATABASE_URL" -f migrations/001_desktop_schema.sql
psql "DATABASE_URL" -f migrations/002_seed_users.sql
psql "DATABASE_URL" -f migrations/003_seed_data.sql
psql "DATABASE_URL" -f migrations/004_create_app_settings.sql
```

**Вариант 2: Локальная PostgreSQL**
1. Установите PostgreSQL: `brew install postgresql@16`
2. Запустите PostgreSQL: `brew services start postgresql@16`
3. Создайте базу данных: `createdb carvix`
4. Выполните миграции:
```bash
psql -U postgres -d carvix -f migrations/001_desktop_schema.sql
psql -U postgres -d carvix -f migrations/002_seed_users.sql
psql -U postgres -d carvix -f migrations/003_seed_data.sql
psql -U postgres -d carvix -f migrations/004_create_app_settings.sql
```
5. Настройте подключение в файле `.env`:
```
DB_NAME=carvix
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Запуск
```bash
python main.py
```

### Тестирование
```bash
pytest tests/ -v
```

## Структура проекта

```
carvix_desktop/
├── main.py                 # Точка входа приложения
├── config.py               # Конфигурация БД и цветовая палитра
├── requirements.txt        # Зависимости Python
├── .env.example           # Пример конфигурации
├── .env                   # Конфигурация (создается пользователем)
├── README.md              # Документация проекта
├── TREE.md                # Дерево проекта
│
└── src/                   # Исходный код
    ├── __init__.py
    ├── database.py        # Пул подключений к PostgreSQL
    ├── models.py          # Модели данных (Employee, Vehicle, Fine, etc.)
    ├── styles.py          # Стили PyQt (бежевая палитра Carvix)
    ├── permissions.py     # Система прав доступа (RBAC)
    ├── validation.py      # Валидация данных
    ├── error_handler.py   # Обработка ошибок
    ├── logger.py          # Система логирования
    ├── settings_manager.py # Управление настройками
    │
    ├── auth/              # Модуль авторизации
    │   ├── __init__.py
    │   └── auth_dialog.py # Диалог авторизации
    │
    ├── api/               # API интеграции
    │   ├── __init__.py
    │   └── gibdd_api.py  # API ГИБДД
    │
    └── ui/                # Модуль пользовательского интерфейса
        ├── __init__.py
        ├── main_window.py      # Главное окно с навигацией
        ├── pages/              # Страницы приложения
        │   ├── __init__.py
        │   ├── dashboard_page.py   # Дашборд с графиками
        │   ├── drivers_page.py     # CRUD водителей
        │   ├── vehicles_page.py    # CRUD ТС
        │   ├── schedule_page.py    # График работы
        │   ├── maintenance_page.py # ТО и Страховка
        │   ├── fines_page.py       # Штрафы
        │   ├── reports_page.py     # Отчеты с графиками
        │   ├── profile_page.py     # Профиль пользователя
        │   ├── users_page.py       # Управление пользователями (админ)
        │   └── settings_page.py    # Настройки (админ)
        │
        └── styles/
            └── styles.qss      # QSS стили (опционально)
│
├── migrations/            # Миграции базы данных
│   ├── 001_desktop_schema.sql
│   ├── 002_seed_users.sql
│   ├── 003_seed_data.sql
│   └── 004_create_app_settings.sql
│
└── tests/                 # Тесты
    ├── __init__.py
    ├── pytest.ini
    ├── test_permissions.py
    ├── test_database.py
    ├── test_auth.py
    ├── test_models.py
    └── test_api.py
```

## Дизайн

Приложение использует дизайн-систему Carvix с бежевой палитрой, соответствующей веб-интерфейсу:

### Цветовая палитра
```python
COLORS = {
    'background': '#FBF8F3',      # Светло-бежевый фон
    'card_background': '#F5EFE3', # Фон карточек
    'text_primary': '#1C1B17',   # Основной текст
    'text_secondary': '#6F6D67', # Вторичный текст
    'accent': '#4A7C59',         # Акцентный зеленый
    'warning': '#e5a00d',         # Предупреждение
    'error': '#C0392B',          # Ошибка
    'success': '#4A7C59',         # Успех
}
```

### Шрифты
- **Основной**: Manrope (UI элементы)
- **Заголовки**: Cormorant Garamond (заголовки карточек)

### Компоненты
- Карточки с закругленными углами (12px)
- Плавные анимации переходов
- Современные кнопки с hover-эффектами
- Таблицы с сортировкой и фильтрацией

## Интеграция с веб-проектом

Desktop-приложение использует ту же базу данных PostgreSQL, что и веб-проект Carvix, обеспечивая единую систему управления автопарком.

### Общие таблицы
- `sotrudnik` - Сотрудники
- `transportnoe_sredstvo` - Транспортные средства
- `work_schedule` - График работы
- `fines` - Штрафы
- `maintenance` - ТО и Страховка

### API интеграция
- GIBDD API для проверки штрафов (mock-реализация)
- Возможность синхронизации с веб-версией

## Безопасность

### Хеширование паролей
- Использование bcrypt для хеирования паролей
- Соль генерируется автоматически для каждого пароля
- Минимальная длина пароля: 6 символов
- Требования к сложности: минимум 1 заглавная, 1 строчная, 1 цифра

### Логирование
- Запись всех попыток входа (успешные и неудачные)
- Логирование действий пользователей
- Логирование ошибок
- Хранение логов в файловой системе

### Тайм-аут сессии
- Автоматический выход после 60 минут бездействия (настраивается)
- Сброс таймера при любом действии пользователя

### RBAC
- Разделение прав по ролям
- Динамическое отображение меню и функционала
- Проверка прав при каждом действии

## Лицензия

© 2024 Carvix. Все права защищены.

