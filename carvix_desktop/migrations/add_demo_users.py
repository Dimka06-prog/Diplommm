#!/usr/bin/env python3
"""
Скрипт миграции: создание/обновление демонстрационных пользователей.
Запуск: python migrations/add_demo_users.py
"""
import sys
sys.path.insert(0, '/Users/dmitrirodkin/PycharmProjects/Diplom_Rodkin/carvix_desktop')

import bcrypt
from src.database import Database

USERS = [
    ('disp', 'Disp123456', 'Иванов Диспетчер', 2, 'DISP001', '+79990001122'),
    ('mech', 'Mech123456', 'Петров Механик', 3, 'MECH001', '+79990003344'),
    ('chief', 'Chief123456', 'Сидоров Главный механик', 4, 'CHIEF001', '+79990005566'),
    ('anal', 'Anal123456', 'Кузнецов Аналитик', 1, 'ANAL001', '+79990007788'),
    ('driver', 'Driver123456', 'Васильев Водитель', 6, 'DRIV001', '+79990009900'),
]

def migrate():
    for login, pwd, fio, rol_id, lic, phone in USERS:
        hash_pwd = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Check if user exists
        existing = Database.execute_query(
            "SELECT id FROM sotrudnik WHERE login = %s", (login,)
        )

        if existing:
            # Update existing user
            Database.execute_query(
                """UPDATE sotrudnik
                   SET fio = %s, parol_hash = %s, rol_id = %s,
                       license_number = %s, phone = %s, podrazdelenie_id = %s
                   WHERE id = %s""",
                (fio, hash_pwd, rol_id, lic, phone, 1, existing[0]['id']),
                fetch=False
            )
            print(f"[OK] Обновлен пользователь: {login} (rol_id={rol_id})")
        else:
            # Insert new user
            Database.execute_query(
                """INSERT INTO sotrudnik (fio, login, parol_hash, license_number, phone, rol_id, podrazdelenie_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (fio, login, hash_pwd, lic, phone, rol_id, 1),
                fetch=False
            )
            print(f"[OK] Создан пользователь: {login} (rol_id={rol_id})")

    print("\nВсе пользователи успешно созданы/обновлены.")

if __name__ == '__main__':
    migrate()
