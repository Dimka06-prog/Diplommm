#!/usr/bin/env python3
"""
Скрипт миграции: добавление тестовых данных для демонстрации.
Запуск: python migrations/add_demo_data.py
"""
import sys
sys.path.insert(0, '/Users/dmitrirodkin/PycharmProjects/Diplom_Rodkin/carvix_desktop')

from datetime import date, timedelta
from src.database import Database


def ensure_marka_model():
    """Создание марок и моделей, если их нет"""
    markas = Database.execute_query("SELECT id, nazvanie FROM marka")
    if not markas:
        Database.execute_query("INSERT INTO marka (nazvanie) VALUES ('Toyota'), ('KAMAZ'), ('GAZ')", fetch=False)
        markas = Database.execute_query("SELECT id, nazvanie FROM marka")
        print("[OK] Созданы марки: Toyota, KAMAZ, GAZ")

    models = Database.execute_query("SELECT id, nazvanie, marka_id FROM model")
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
        models = Database.execute_query("SELECT id, nazvanie, marka_id FROM model")
        print("[OK] Созданы модели")
    return markas, models


def add_vehicles(markas, models):
    """Добавление транспортных средств"""
    existing = Database.execute_query("SELECT COUNT(*) as cnt FROM transportnoe_sredstvo")
    if existing and existing[0]['cnt'] >= 6:
        print("[SKIP] ТС уже существуют")
        return

    marka_ids = {m['nazvanie']: m['id'] for m in markas}
    models_data = Database.execute_query("""
        SELECT m.id, m.nazvanie, ma.nazvanie as marka_name
        FROM model m JOIN marka ma ON m.marka_id = ma.id
    """)

    vehicles = [
        ('А123ВС77', 'INV001', 'XTA210930Y2768029', 45000, 'Активно'),
        ('В456НК99', 'INV002', 'XTA210930Y2768030', 32000, 'Активно'),
        ('Е789ОР50', 'INV003', 'XTA210930Y2768031', 78000, 'На ремонте'),
        ('К012МН77', 'INV004', 'XTA210930Y2768032', 120000, 'Активно'),
        ('М345РС99', 'INV005', 'XTA210930Y2768033', 56000, 'Активно'),
        ('Н678ТВ50', 'INV006', 'XTA210930Y2768034', 89000, 'Активно'),
    ]

    # Get driver IDs (rol_id=6 or rol_id=7)
    drivers = Database.execute_query("SELECT id FROM sotrudnik WHERE rol_id IN (2, 6, 7)")
    driver_ids = [d['id'] for d in drivers] if drivers else []

    # Get podrazdelenie id
    depts = Database.execute_query("SELECT id FROM podrazdelenie LIMIT 1")
    dept_id = depts[0]['id'] if depts else None

    for i, (gos, inv, vin, probeg, status) in enumerate(vehicles):
        model_id = models_data[i % len(models_data)]['id'] if models_data else None
        driver_id = driver_ids[i % len(driver_ids)] if driver_ids else None

        # Check if already exists
        existing = Database.execute_query("SELECT id FROM transportnoe_sredstvo WHERE gos_nomer = %s", (gos,))
        if existing:
            continue

        Database.execute_query(
            """INSERT INTO transportnoe_sredstvo
            (gos_nomer, invent_nomer, vin, probeg, model_id, podrazdelenie_id, assigned_driver_id, tekuschee_sostoyanie,
             to_expiry, insurance_expiry)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (gos, inv, vin, probeg, model_id, dept_id, driver_id, status,
             date.today() + timedelta(days=30+i*5), date.today() + timedelta(days=60+i*10)),
            fetch=False
        )
    print("[OK] ТС созданы")


def add_fines():
    """Добавление штрафов"""
    existing = Database.execute_query("SELECT COUNT(*) as cnt FROM fines")
    if existing and existing[0]['cnt'] >= 8:
        print("[SKIP] Штрафы уже существуют")
        return

    vehicles = Database.execute_query("SELECT id, gos_nomer FROM transportnoe_sredstvo")
    if not vehicles:
        print("[SKIP] Нет ТС для создания штрафов")
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
    ]

    for i, (veh_idx, amount, desc, status, post_num) in enumerate(fines_data):
        veh = vehicles[veh_idx % len(vehicles)]
        fine_date = date.today() - timedelta(days=i*3)

        # Check if already exists by postanovlenie_number
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
    print("[OK] Штрафы созданы")


def add_schedules():
    """Добавление смен в график работы"""
    existing = Database.execute_query("SELECT COUNT(*) as cnt FROM work_schedule")
    if existing and existing[0]['cnt'] >= 10:
        print("[SKIP] Смены уже существуют")
        return

    drivers = Database.execute_query("SELECT id FROM sotrudnik WHERE rol_id IN (2, 6, 7)")
    vehicles = Database.execute_query("SELECT id FROM transportnoe_sredstvo")

    if not drivers or not vehicles:
        print("[SKIP] Нет водителей или ТС для создания смен")
        return

    shifts = [
        ('08:00', '20:00', 'Запланирована'),
        ('09:00', '21:00', 'Выполнена'),
        ('10:00', '22:00', 'Запланирована'),
        ('08:00', '20:00', 'Выполнена'),
        ('09:00', '21:00', 'Запланирована'),
    ]

    for i in range(12):
        driver = drivers[i % len(drivers)]
        veh = vehicles[i % len(vehicles)]
        shift = shifts[i % len(shifts)]
        sch_date = date.today() - timedelta(days=5) + timedelta(days=i)

        # Check if already exists
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
    print("[OK] Смены созданы")


def migrate():
    print("=== Добавление тестовых данных ===")
    markas, models = ensure_marka_model()
    add_vehicles(markas, models)
    add_fines()
    add_schedules()
    print("\n=== Готово ===")


if __name__ == '__main__':
    migrate()
