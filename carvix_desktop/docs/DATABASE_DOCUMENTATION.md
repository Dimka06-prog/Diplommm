# Документация глобальной базы данных Carvix

## Обзор

Глобальная база данных PostgreSQL используется всеми компонентами экосистемы Carvix:
- **Desktop-приложение** (PyQt6)
- **Web-приложение** (Django/Flask)
- **Мобильное приложение** (React Native)

База данных размещена на облачной платформе Render.com с поддержкой SSL-шифрования для обеспечения безопасности передачи данных.

## Технические характеристики

### Характеристики сервера
- **Платформа:** Render.com
- **Тип базы данных:** PostgreSQL
- **Версия PostgreSQL:** 14+
- **Режим работы:** 24/7
- **SSL-шифрование:** Включено

### Подключение
- **Протокол:** PostgreSQL с SSL
- **Пул соединений:** Поддерживается в desktop-приложении
- **Таймауты:** Настраиваемые для каждого приложения

## Структура базы данных

### Основные таблицы

#### 1. `rol` - Роли пользователей
```sql
CREATE TABLE rol (
    id INTEGER PRIMARY KEY,
    nazvanie VARCHAR(50) NOT NULL UNIQUE
);
```

**Роли в системе:**
- ID 1: Аналитик
- ID 2: Диспетчер
- ID 3: Механик
- ID 4: Главный механик
- ID 5: Директор (Администратор)
- ID 6: Водитель

#### 2. `podrazdelenie` - Подразделения
```sql
CREATE TABLE podrazdelenie (
    id INTEGER PRIMARY KEY,
    nazvanie VARCHAR(100) NOT NULL
);
```

#### 3. `sotrudnik` - Сотрудники
```sql
CREATE TABLE sotrudnik (
    id INTEGER PRIMARY KEY,
    fio VARCHAR(100) NOT NULL,
    login VARCHAR(50) NOT NULL UNIQUE,
    parol_hash VARCHAR(255) NOT NULL,
    rol_id INTEGER NOT NULL REFERENCES rol(id),
    podrazdelenie_id INTEGER REFERENCES podrazdelenie(id),
    license_number VARCHAR(20),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Индексы:**
- UNIQUE INDEX на login
- INDEX на rol_id
- INDEX на podrazdelenie_id

#### 4. `transportnoe_sredstvo` - Транспортные средства
```sql
CREATE TABLE transportnoe_sredstvo (
    id INTEGER PRIMARY KEY,
    gos_nomer VARCHAR(20) NOT NULL UNIQUE,
    invent_nomer VARCHAR(20) NOT NULL,
    vin VARCHAR(17),
    marka VARCHAR(50),
    model VARCHAR(50),
    god_vypuska INTEGER,
    probeg INTEGER DEFAULT 0,
    tekuschee_sostoyanie VARCHAR(50) DEFAULT 'Активно',
    podrazdelenie_id INTEGER REFERENCES podrazdelenie(id),
    assigned_driver_id INTEGER REFERENCES sotrudnik(id),
    insurance_expiry DATE,
    to_expiry DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Индексы:**
- UNIQUE INDEX на gos_nomer
- INDEX на assigned_driver_id
- INDEX на podrazделение_id

#### 5. `work_schedule` - График работы
```sql
CREATE TABLE work_schedule (
    id INTEGER PRIMARY KEY,
    driver_id INTEGER NOT NULL REFERENCES sotrudnik(id),
    ts_id INTEGER REFERENCES transportnoe_sredstvo(id),
    date DATE NOT NULL,
    shift_start TIME NOT NULL,
    shift_end TIME NOT NULL,
    status VARCHAR(50) DEFAULT 'Запланирована'
);
```

**Индексы:**
- INDEX на driver_id
- INDEX на ts_id
- INDEX на date

#### 6. `maintenance` - Техническое обслуживание
```sql
CREATE TABLE maintenance (
    id INTEGER PRIMARY KEY,
    ts_id INTEGER NOT NULL REFERENCES transportnoe_sredstvo(id),
    date DATE NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    cost DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'Запланировано'
);
```

**Индексы:**
- INDEX на ts_id
- INDEX на date

#### 7. `fines` - Штрафы
```sql
CREATE TABLE fines (
    id INTEGER PRIMARY KEY,
    ts_id INTEGER REFERENCES transportnoe_sredstvo(id),
    date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'Не оплачен',
    postanovlenie_number VARCHAR(50)
);
```

**Индексы:**
- INDEX на ts_id
- INDEX на date
- INDEX на status

#### 8. `app_settings` - Настройки приложения
```sql
CREATE TABLE app_settings (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Безопасность данных

### Шифрование паролей
- Алгоритм: bcrypt
- Соль: Генерируется автоматически (bcrypt.gensalt)
- Хранение: Хешированные пароли в поле `parol_hash`

### SSL-шифрование
- Все соединения к базе данных используют SSL
- Сертификаты управляются Render.com
- Принудительное SSL-подключение в приложениях

### Права доступа
- RBAC (Role-Based Access Control)
- 6 ролей с различными правами доступа
- Проверка прав на уровне приложения

## Интеграция между приложениями

### Desktop-приложение
- **Язык:** Python
- **Библиотека:** psycopg2
- **Пул соединений:** Реализован
- **Кэширование:** Локальное кэширование настроек

### Web-приложение
- **Язык:** Python (Django/Flask)
- **ORM:** Django ORM / SQLAlchemy
- **API:** REST API для мобильного приложения
- **WebSocket:** Реальное время обновлений

### Мобильное приложение
- **Язык:** JavaScript/TypeScript (React Native)
- **API:** REST API от web-приложения
- **Офлайн-режим:** Локальное хранилище с синхронизацией

## Резервное копирование и восстановление

### Стратегия резервного копирования
- **Автоматические бэкапы:** Ежедневно
- **Хранение:** 7 дней
- **Регион:** США (Render.com)
- **Шифрование бэкапов:** Включено

### Восстановление
- **Время восстановления:** ~5 минут
- **Точка восстановления:** На момент последнего бэкапа
- **Процедура:** Через панель управления Render.com

## Мониторинг и логирование

### Метрики производительности
- **Количество соединений:** Мониторинг в реальном времени
- **Время выполнения запросов:** Логирование медленных запросов
- **Размер базы данных:** Мониторинг роста

### Логи
- **Логи запросов:** Включены
- **Логи ошибок:** Включены
- **Хранение логов:** 30 дней

## Масштабирование

### Горизонтальное масштабирование
- **Read replicas:** Поддерживается
- **Load balancing:** На уровне приложения

### Вертикальное масштабирование
- **Увеличение ресурсов:** Через панель Render.com
- **Оптимизация запросов:** Регулярный анализ

## Миграции и обновления

### Версионирование схемы
- **Инструмент:** SQL-скрипты в папке migrations/
- **Идемпотентность:** Все миграции идемпотентны
- **Откат:** Поддерживается для критических изменений

### Процесс миграции
1. Создание SQL-скрипта миграции
2. Тестирование на тестовой базе
3. Применение на продакшн
4. Проверка данных
5. Подтверждение успешного применения

## Оптимизация производительности

### Индексы
- Все внешние ключи проиндексированы
- Часто используемые поля в WHERE проиндексированы
- Регулярный анализ использования индексов

### Запросы
- Оптимизация JOIN-операций
- Использование prepared statements
- Кэширование часто запрашиваемых данных

### Пул соединений
- Минимальное количество: 2
- Максимальное количество: 10
- Таймаут простоя: 300 секунд

## Безопасность на уровне приложения

### Валидация данных
- Валидация на уровне приложения
- Проверка типов данных
- Защита от SQL-инъекций (prepared statements)

### Аудит
- Логирование всех изменений данных
- Запись пользователя, времени и типа операции
- Хранение логов аудита в отдельной таблице

## Будущие улучшения

### Планируемые изменения
- Добавление таблицы для геолокации ТС
- Реализация soft delete для критических данных
- Добавление системы уведомлений
- Интеграция с внешними API (ГИБДД, страховые компании)

### Оптимизация
- Разделение на read/write базы
- Реализация кэширования на уровне Redis
- Оптимизация сложных аналитических запросов

## Контактная информация

### Администрирование
- **Администратор БД:** Системный администратор
- **Поддержка:** Через панель Render.com
- **Экстренные случаи:** 24/7 поддержка Render.com

---

## Архитектура Desktop-приложения

### Структура проекта
```
carvix_desktop/
├── main.py                     # Точка входа, SplashScreen, CarvixApp
├── src/
│   ├── database.py             # Connection pool (psycopg2), lazy init
│   ├── styles.py               # Единая QSS-таблица стилей, шрифты
│   ├── permissions.py          # RBAC: 6 ролей, 15+ пермишенов
│   ├── validation.py           # Валидация ФИО, телефона, пароля
│   ├── logger.py               # Логирование входов/выходов/ошибок
│   ├── error_handler.py        # Кастомные исключения + обработка
│   ├── settings_manager.py     # Чтение/запись app_settings из БД
│   ├── api/
│   │   └── gibdd_api.py        # Заглушка API ГИБДД + NotificationSystem
│   └── ui/
│       ├── main_window.py      # Боковая панель, заголовок, навигация
│       ├── pages/
│       │   ├── dashboard_page.py   # Карточки статистики + bar charts
│       │   ├── drivers_page.py     # Таблица водителей + поиск
│       │   ├── vehicles_page.py    # Таблица ТС + поиск
│       │   ├── schedule_page.py    # График работы + поиск
│       │   ├── maintenance_page.py # ТО/страховка + напоминания
│       │   ├── fines_page.py       # Штрафы + синхронизация с ГИБДД
│       │   ├── reports_page.py     # Отчеты с графиками
│       │   ├── profile_page.py     # Профиль + смена пароля
│       │   ├── users_page.py       # Управление пользователями
│       │   └── settings_page.py    # Системные настройки
```

### Ключевые технические решения
- **Lazy loading:** Страницы создаются при первом открытии, не при старте
- **Deferred refresh:** `refresh_data()` вызывается через `QTimer.singleShot(0)`
- **Splash screen:** Мгновенная обратная связь при запуске
- **Безопасность:** bcrypt-хеширование, SSL, prepared statements
- **Поиск:** Поле поиска на всех страницах с таблицами
- **Шрифты:** Georgia (системный) вместо Cormorant Garamond

---

*Документация актуальна на: 2026-05-27*
*Версия схемы: 1.1*
