#!/usr/bin/env python3
"""
Скрипт: добавление тестовых данных для демо-пользователей.
Запуск: python3 migrations/add_demo_data_for_test_users.py
"""
import sys
sys.path.insert(0, '/Users/dmitrirodkin/PycharmProjects/Diplom_Rodkin/carvix_desktop')

from datetime import date, timedelta
from src.database import Database

# Test user logins
TEST_USERS = {
    'disp': 2,      # dispatcher
    'mech': 3,      # mechanic
    'chief': 4,     # chief mechanic
    'anal': 1,      # analyst
    'driver': 6,    # driver
}


def get_user_ids():
    """Получить ID демо-пользователей из БД"""
    users = {}
    for login, expected_rol_id in TEST_USERS.items():
        result = Database.execute_query(
            "SELECT id, rol_id FROM sotrudnik WHERE login = %s", (login,)
        )
        if result:
            users[login] = result[0]
    return users


def ensure_marka_model():
    """Создание марок и моделей"""
    markas = Database.execute_query("SELECT id, nazvanie FROM marka")
    if not markas:
        Database.execute_query(
            "INSERT INTO marka (nazvanie) VALUES ('Toyota'), ('KAMAZ'), ('GAZ')",
            fetch=False
        )
        markas = Database.execute_query("SELECT id, nazvanie FROM marka")
        print("[OK] Созданы марки")

    models = Database.execute_query("SELECT id FROM model")
    if not models:
        marka_ids = {m['nazvanie']: m['id'] for m in markas}
        Database.execute_query(
            """INSERT INTO model (nazvanie, marka_id) VALUES
            ('Camry', %s), ('Hilux', %s),
            ('43118', %s), ('65115', %s),
            ('GAZelle', %s), ('Sobol', %s)""",
            (marka_ids.get('Toyota'), marka_ids.get('Toyota'),
             marka_ids.get('KAMAZ'), marka_ids.get('KAMAZ'),
             marka_ids.get('GAZ'), marka_ids.get('GAZ')),
            fetch=False
        )
        print("[OK] Созданы модели")
    return markas


def add_vehicles_for_users(users):
    """Добавление ТС и привязка к тестовым водителям"""
    models = Database.execute_query("SELECT id FROM model")
    if not models:
        print("[SKIP] Нет моделей для создания ТС")
        return []

    # Get dispatcher/dept IDs
    depts = Database.execute_query("SELECT id FROM podrazdelenie LIMIT 1")
    dept_id = depts[0]['id'] if depts else None

    # Get driver IDs (rol_id=2=dispatcher can also be driver in this context, plus rol_id=6,7)
    all_drivers = Database.execute_query(
        "SELECT id, login FROM sotrudnik WHERE rol_id IN (2, 6, 7)"
    )
    driver_map = {d['login']: d['id'] for d in all_drivers}

    vehicles_data = [
        ('А123ВС77', 'INV001', 'XTA210930Y2768029', 45000, 'Активно'),
        ('В456НК99', 'INV002', 'XTA210930Y2768030', 32000, 'Активно'),
        ('Е789ОР50', 'INV003', 'XTA210930Y2768031', 78000, 'На ремонте'),
        ('К012МН77', 'INV004', 'XTA210930Y2768032', 120000, 'Активно'),
        ('М345РС99', 'INV005', 'XTA210930Y2768033', 56000, 'Активно'),
        ('Н678ТВ50', 'INV006', 'XTA210930Y2768034', 89000, 'Активно'),
        ('П901СЕ77', 'INV007', 'XTA210930Y2768035', 67000, 'Активно'),
        ('Р234УК99', 'INV008', 'XTA210930Y2768036', 43000, 'На ремонте'),
    ]

    created_vehicles = []
    for i, (gos, inv, vin, probeg, status) in enumerate(vehicles_data):
        # Check if already exists
        existing = Database.execute_query(
            "SELECT id FROM transportnoe_sredstvo WHERE gos_nomer = %s", (gos,)
        )
        if existing:
            created_vehicles.append(existing[0]['id'])
            continue

        model_id = models[i % len(models)]['id']
        # Assign driver: try 'driver' test user first, then rotate
        driver_id = None
        if 'driver' in driver_map and i < 4:
            driver_id = driver_map['driver']
        elif i < len(all_drivers):
            driver_id = all_drivers[i % len(all_drivers)]['id']

        result = Database.execute_query(
            """INSERT INTO transportnoe_sredstvo
            (gos_nomer, invent_nomer, vin, probeg, model_id, podrazdelenie_id,
             assigned_driver_id, tekuschee_sostoyanie, to_expiry, insurance_expiry)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id""",
            (gos, inv, vin, probeg, model_id, dept_id, driver_id, status,
             date.today() + timedelta(days=15 + i*5), date.today() + timedelta(days=45 + i*10)),
            fetch=False
        )
        # Get the inserted ID
        new_id = Database.execute_query(
            "SELECT id FROM transportnoe_sredstvo WHERE gos_nomer = %s", (gos,)
        )
        if new_id:
            created_vehicles.append(new_id[0]['id'])
            print(f"[OK] ТС создан: {gos}")

    return created_vehicles


def add_fines_for_vehicles():
    """Добавление штрафов для ТС"""
    vehicles = Database.execute_query("SELECT id, gos_nomer FROM transportnoe_sredstvo")
    if not vehicles:
        print("[SKIP] Нет ТС для штрафов")
        return

    fines_data = [
        (0, 1500.00, 'Превышение скорости', 'Не оплачен', '1881017726052014'),
        (1, 500.00, 'Неправильная парковка', 'Оплачен', '1881017726052015'),
        (2, 2500.00, 'Проезд на красный', 'Не оплачен', '1881017726052016'),
        (3, 800.00, 'Превышение скорости', 'Оплачен', '1881017726052017'),
        (4, 3000.00, 'Проезд на красный', 'В обработке', '1881017726052018'),
        (5, 1000.00, 'Неправильная парковка', 'Не оплачен', '1881017726052019'),
        (0, 2000.00, 'Превышение скорости', 'Оплачен', '1881017726052020'),
        (3, 1500.00, 'Проезд на красный', 'Не оплачен', '1881017726052021'),
        (1, 3500.00, 'Проезд на красный', 'Не оплачен', '1881017726052022'),
        (5, 500.00, 'Неправильная парковка', 'Оплачен', '1881017726052023'),
        (2, 1200.00, 'Превышение скорости', 'Оплачен', '1881017726052024'),
        (4, 4500.00, 'Проезд на красный', 'Не оплачен', '1881017726052025'),
    ]

    added = 0
    for i, (veh_idx, amount, desc, status, post_num) in enumerate(fines_data):
        veh = vehicles[veh_idx % len(vehicles)]
        fine_date = date.today() - timedelta(days=i*5)

        # Check if exists
        existing = Database.execute_query(
            "SELECT id FROM fines WHERE postanovlenie_number = %s", (post_num,)
        )
        if existing:
            continue

        Database.execute_query(
            """INSERT INTO fines (ts_id, date, amount, description, status, postanovlenie_number)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (veh['id'], fine_date, amount, desc, status, post_num),
            fetch=False
        )
        added += 1

    print(f"[OK] Штрафов добавлено: {added}")


def add_schedules_for_users(users):
    """Добавление смен для водителей"""
    # Get all potential drivers (rol_id 2, 6, 7)
    all_drivers = Database.execute_query(
        "SELECT id, login FROM sotrudnik WHERE rol_id IN (2, 6, 7)"
    )
    vehicles = Database.execute_query("SELECT id FROM transportnoe_sredstvo")

    if not all_drivers or not vehicles:
        print("[SKIP] Нет водителей или ТС")
        return

    shifts = [
        ('08:00', '20:00', 'Запланирована'),
        ('09:00', '21:00', 'Выполнена'),
        ('10:00', '22:00', 'Запланирована'),
        ('08:00', '20:00', 'Выполнена'),
        ('09:00', '21:00', 'Запланирована'),
        ('10:00', '22:00', 'Выполнена'),
    ]

    added = 0
    for i in range(18):
        driver = all_drivers[i % len(all_drivers)]
        veh = vehicles[i % len(vehicles)]
        shift = shifts[i % len(shifts)]
        sch_date = date.today() - timedelta(days=7) + timedelta(days=i)

        # Check if exists
        existing = Database.execute_query(
            "SELECT id FROM work_schedule WHERE driver_id = %s AND date = %s",
            (driver['id'], sch_date)
        )
        if existing:
            continue

        Database.execute_query(
            """INSERT INTO work_schedule (driver_id, ts_id, date, shift_start, shift_end, status)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (driver['id'], veh['id'], sch_date, shift[0], shift[1], shift[2]),
            fetch=False
        )
        added += 1

    print(f"[OK] Смен добавлено: {added}")


def verify_data():
    """Проверка созданных данных"""
    stats = {}
    stats['users'] = Database.execute_query("SELECT COUNT(*) as cnt FROM sotrudnik")[0]['cnt']
    stats['vehicles'] = Database.execute_query("SELECT COUNT(*) as cnt FROM transportnoe_sredstvo")[0]['cnt']
    stats['fines'] = Database.execute_query("SELECT COUNT(*) as cnt FROM fines")[0]['cnt']
    stats['schedules'] = Database.execute_query("SELECT COUNT(*) as cnt FROM work_schedule")[0]['cnt']

    print("\n=== Статистика в БД ===")
    print(f"Пользователей: {stats['users']}")
    print(f"ТС: {stats['vehicles']}")
    print(f"Штрафов: {stats['fines']}")
    print(f"Смен: {stats['schedules']}")
    return stats


def migrate():
    print("=== Добавление тестовых данных для демо-пользователей ===")
    users = get_user_ids()
    print(f"Найдено тестовых пользователей: {list(users.keys())}")

    ensure_marka_model()
    add_vehicles_for_users(users)
    add_fines_for_vehicles()
    add_schedules_for_users(users)
    verify_data()
    print("\n=== Готово ===")


if __name__ == '__main__':
    migrate()
