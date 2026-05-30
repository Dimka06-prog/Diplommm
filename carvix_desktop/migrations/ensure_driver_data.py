#!/usr/bin/env python3
"""
Скрипт: гарантированное создание смен и штрафов для водителя 'driver'.
Запускать из PyCharm или через: python migrations/ensure_driver_data.py
"""
import sys
sys.path.insert(0, '/Users/dmitrirodkin/PycharmProjects/Diplom_Rodkin/carvix_desktop')

from datetime import date, timedelta
from src.database import Database


def ensure_driver_data():
    # 1. Найти водителя 'driver'
    driver = Database.execute_query(
        "SELECT id, fio, rol_id FROM sotrudnik WHERE login = %s",
        ('driver',)
    )
    if not driver:
        print("[ERROR] Пользователь 'driver' не найден в БД!")
        return

    driver_id = driver[0]['id']
    print(f"[INFO] Найден driver: id={driver_id}, fio={driver[0]['fio']}, rol_id={driver[0]['rol_id']}")

    # 2. Найти или назначить ТС для водителя
    vehicles = Database.execute_query(
        "SELECT id, gos_nomer FROM transportnoe_sredstvo WHERE assigned_driver_id = %s",
        (driver_id,)
    )

    if not vehicles:
        # Назначить свободное ТС
        free_veh = Database.execute_query(
            "SELECT id, gos_nomer FROM transportnoe_sredstvo WHERE assigned_driver_id IS NULL LIMIT 2"
        )
        if free_veh:
            for v in free_veh:
                Database.execute_query(
                    "UPDATE transportnoe_sredstvo SET assigned_driver_id = %s WHERE id = %s",
                    (driver_id, v['id']),
                    fetch=False
                )
                print(f"[OK] ТС {v['gos_nomer']} назначено driver")
            vehicles = Database.execute_query(
                "SELECT id, gos_nomer FROM transportnoe_sredstvo WHERE assigned_driver_id = %s",
                (driver_id,)
            )
        else:
            # Создать новое ТС
            markas = Database.execute_query("SELECT id FROM marka LIMIT 1")
            models = Database.execute_query("SELECT id FROM model LIMIT 1")
            depts = Database.execute_query("SELECT id FROM podrazdelenie LIMIT 1")
            marka_id = markas[0]['id'] if markas else None
            model_id = models[0]['id'] if models else None
            dept_id = depts[0]['id'] if depts else None

            new_gos = 'ВОД77777'
            Database.execute_query(
                """INSERT INTO transportnoe_sredstvo
                (gos_nomer, invent_nomer, vin, probeg, model_id, podrazdelenie_id,
                 assigned_driver_id, tekuschee_sostoyanie, to_expiry, insurance_expiry)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (new_gos, 'INV_DRV', 'XTA0000000000001', 25000, model_id, dept_id, driver_id,
                 'Активно', date.today() + timedelta(days=30), date.today() + timedelta(days=90)),
                fetch=False
            )
            print(f"[OK] Создано новое ТС {new_gos} для driver")
            vehicles = Database.execute_query(
                "SELECT id, gos_nomer FROM transportnoe_sredstvo WHERE assigned_driver_id = %s",
                (driver_id,)
            )

    print(f"[INFO] ТС водителя: {len(vehicles)}")
    for v in vehicles:
        print(f"  - {v['gos_nomer']} (id={v['id']})")

    # 3. Создать смены для водителя
    existing_schedules = Database.execute_query(
        "SELECT COUNT(*) as cnt FROM work_schedule WHERE driver_id = %s",
        (driver_id,)
    )
    print(f"[INFO] Существующих смен: {existing_schedules[0]['cnt']}")

    veh_ids = [v['id'] for v in vehicles]
    shifts = [
        ('08:00', '20:00', 'Запланирована'),
        ('09:00', '21:00', 'Выполнена'),
        ('10:00', '22:00', 'Запланирована'),
        ('08:00', '20:00', 'Выполнена'),
        ('09:00', '21:00', 'Выполнена'),
    ]

    added_shifts = 0
    for i in range(5):
        sch_date = date.today() - timedelta(days=3) + timedelta(days=i)
        existing = Database.execute_query(
            "SELECT id FROM work_schedule WHERE driver_id = %s AND date = %s",
            (driver_id, sch_date)
        )
        if existing:
            continue

        veh_id = veh_ids[i % len(veh_ids)]
        shift = shifts[i % len(shifts)]
        Database.execute_query(
            """INSERT INTO work_schedule (driver_id, ts_id, date, shift_start, shift_end, status)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (driver_id, veh_id, sch_date, shift[0], shift[1], shift[2]),
            fetch=False
        )
        added_shifts += 1
    print(f"[OK] Смен добавлено: {added_shifts}")

    # 4. Создать штрафы для ТС водителя
    fines_data = [
        (1500.00, 'Превышение скорости', 'Не оплачен', '1881017726053001'),
        (500.00, 'Неправильная парковка', 'Оплачен', '1881017726053002'),
        (2500.00, 'Проезд на красный', 'Не оплачен', '1881017726053003'),
        (800.00, 'Превышение скорости', 'Оплачен', '1881017726053004'),
        (3000.00, 'Проезд на красный', 'В обработке', '1881017726053005'),
    ]

    added_fines = 0
    for i, (amount, desc, status, post_num) in enumerate(fines_data):
        veh_id = veh_ids[i % len(veh_ids)]
        fine_date = date.today() - timedelta(days=i*2)

        existing = Database.execute_query(
            "SELECT id FROM fines WHERE postanovlenie_number = %s",
            (post_num,)
        )
        if existing:
            continue

        Database.execute_query(
            """INSERT INTO fines (ts_id, date, amount, description, status, postanovlenie_number)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (veh_id, fine_date, amount, desc, status, post_num),
            fetch=False
        )
        added_fines += 1
    print(f"[OK] Штрафов добавлено: {added_fines}")

    # 5. Итоговая проверка
    final_schedules = Database.execute_query(
        "SELECT COUNT(*) as cnt FROM work_schedule WHERE driver_id = %s", (driver_id,)
    )
    final_vehicles = Database.execute_query(
        "SELECT COUNT(*) as cnt FROM transportnoe_sredstvo WHERE assigned_driver_id = %s", (driver_id,)
    )
    veh_ids = Database.execute_query(
        "SELECT id FROM transportnoe_sredstvo WHERE assigned_driver_id = %s", (driver_id,)
    )
    final_fines = 0
    if veh_ids:
        if len(veh_ids) == 1:
            fc = Database.execute_query("SELECT COUNT(*) as cnt FROM fines WHERE ts_id = %s", (veh_ids[0]['id'],))
        else:
            ph = ','.join(['%s'] * len(veh_ids))
            ids = tuple(v['id'] for v in veh_ids)
            fc = Database.execute_query(f"SELECT COUNT(*) as cnt FROM fines WHERE ts_id IN ({ph})", ids)
        final_fines = fc[0]['cnt']

    print("\n=== Итог для driver ===")
    print(f"ТС: {final_vehicles[0]['cnt']}")
    print(f"Смен: {final_schedules[0]['cnt']}")
    print(f"Штрафов: {final_fines}")
    print("========================\n")


if __name__ == '__main__':
    ensure_driver_data()
