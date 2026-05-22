#!/usr/bin/env python3
"""
Seed database with test data for 4 roles (50 rows each)
"""

import psycopg2
import random
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def seed_database():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Get role IDs
        cursor.execute("SELECT id, nazvanie FROM rol")
        roles = {row[1]: row[0] for row in cursor.fetchall()}
        print(f"Available roles: {roles}")
        
        # Get or create default department
        cursor.execute("SELECT id FROM podrazdelenie LIMIT 1")
        dept = cursor.fetchone()
        if not dept:
            cursor.execute("""
                INSERT INTO podrazdelenie (nazvanie)
                VALUES ('Транспортный цех')
                RETURNING id
            """)
            dept = cursor.fetchone()
        dept_id = dept[0]
        
        # Get vehicle IDs
        cursor.execute("SELECT id, gos_nomer FROM transportnoe_sredstvo")
        vehicles = cursor.fetchall()
        
        # Seed 50 employees across 4 roles - use available roles
        roles_list = list(roles.keys())[:4]  # Use first 4 available roles
        if len(roles_list) < 4:
            print(f"Warning: Only {len(roles_list)} roles available")
        first_names = ['Иван', 'Петр', 'Сергей', 'Алексей', 'Дмитрий', 'Андрей', 'Михаил', 'Николай', 'Александр', 'Владимир']
        last_names = ['Иванов', 'Петров', 'Сидоров', 'Козлов', 'Новиков', 'Морозов', 'Волков', 'Соколов', 'Лебедев', 'Кузнецов']

        # Create simple 3-character logins and passwords
        simple_logins = ['abc', 'def', 'ghi', 'jkl', 'mno', 'pqr', 'stu', 'vwx', 'yz1', '234']

        print("Seeding employees...")
        for i in range(50):
            role = roles_list[i % 4]
            fio = f"{first_names[i % 10]} {last_names[i % 10]} {i+1}"
            login = simple_logins[i % 10] + str(i // 10)  # 3 chars + number
            password = hash_password("123")  # Simple 3-character password
            license_number = f"{random.randint(10000, 99999)}"
            phone = f"+7{random.randint(9000000000, 9999999999)}"

            cursor.execute("""
                INSERT INTO sotrudnik (fio, login, parol_hash, license_number, phone, rol_id, podrazdelenie_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (login) DO NOTHING
            """, (fio, login, password, license_number, phone, roles[role], dept_id, datetime.now()))
        
        # Get all employee IDs - use available roles
        # Find driver-like role (Пользователь or Диспетчер)
        driver_role_id = roles.get('Пользователь', roles.get('Диспетчер', list(roles.values())[0]))
        cursor.execute("SELECT id FROM sotrudnik WHERE rol_id = %s", (driver_role_id,))
        drivers = [row[0] for row in cursor.fetchall()]
        
        # Find mechanic-like role
        mechanic_role_id = roles.get('Механик', list(roles.values())[0])
        cursor.execute("SELECT id FROM sotrudnik WHERE rol_id = %s", (mechanic_role_id,))
        mechanics = [row[0] for row in cursor.fetchall()]
        
        # Get or create model
        cursor.execute("SELECT id FROM model LIMIT 1")
        model = cursor.fetchone()
        if not model:
            # Create marka and model
            cursor.execute("INSERT INTO marka (nazvanie) VALUES ('Toyota') RETURNING id")
            marka_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO model (nazvanie, marka_id) VALUES ('Camry', %s) RETURNING id", (marka_id,))
            model = cursor.fetchone()
        model_id = model[0]
        
        # Seed 50 vehicles
        print("Seeding vehicles...")
        for i in range(50):
            gos_nomer = f"{random.choice(['А', 'В', 'Е', 'К', 'М', 'Н', 'О', 'Р', 'С', 'Т', 'У', 'Х'])}{random.randint(100, 999)}{random.choice(['А', 'В', 'Е', 'К', 'М', 'Н', 'О', 'Р', 'С', 'Т', 'У', 'Х'])}{random.randint(100, 199)}"
            invent_nomer = f"INV-{random.randint(10000, 99999)}"
            # VIN must be exactly 17 characters
            vin = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=17))
            probeg = random.randint(10000, 200000)
            to_expiry = datetime.now() + timedelta(days=random.randint(-30, 365))
            insurance_expiry = datetime.now() + timedelta(days=random.randint(30, 730))
            assigned_driver = random.choice(drivers) if drivers else None
            
            cursor.execute("""
                INSERT INTO transportnoe_sredstvo (gos_nomer, invent_nomer, vin, probeg, to_expiry, insurance_expiry, assigned_driver_id, model_id, podrazdelenie_id, tekuschee_sostoyanie, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (gos_nomer, invent_nomer, vin, probeg, to_expiry, insurance_expiry, assigned_driver, model_id, dept_id, 'Активно', datetime.now()))
        
        # Refresh vehicle list
        cursor.execute("SELECT id FROM transportnoe_sredstvo")
        vehicle_ids = [row[0] for row in cursor.fetchall()]
        
        # Seed 50 fines
        print("Seeding fines...")
        statuses = ['Не оплачен', 'Оплачен', 'В обработке']
        for i in range(50):
            ts_id = random.choice(vehicle_ids)
            date = datetime.now() - timedelta(days=random.randint(1, 365))
            amount = random.randint(500, 5000)
            description = random.choice(['Превышение скорости', 'Неправильная парковка', 'Проезд на красный', 'Не пристегнут ремень', 'Использование телефона'])
            status = random.choice(statuses)
            postanovlenie_number = f"{random.randint(100000, 999999)}"
            
            cursor.execute("""
                INSERT INTO fines (ts_id, date, amount, description, status, postanovlenie_number, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (ts_id, date, amount, description, status, postanovlenie_number, datetime.now()))
        
        # Seed 50 work schedules
        print("Seeding work schedules...")
        schedule_statuses = ['Запланировано', 'Выполнено', 'Отменено']
        for i in range(50):
            ts_id = random.choice(vehicle_ids)
            driver_id = random.choice(drivers) if drivers else None
            date = datetime.now() + timedelta(days=random.randint(-30, 90))
            shift_start = f"{random.randint(6, 9)}:00"
            shift_end = f"{random.randint(17, 20)}:00"
            status = random.choice(schedule_statuses)
            
            cursor.execute("""
                INSERT INTO work_schedule (ts_id, driver_id, date, shift_start, shift_end, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (ts_id, driver_id, date, shift_start, shift_end, status, datetime.now()))
        
        # Seed 50 maintenance records
        print("Seeding maintenance records...")
        maintenance_types = ['ТО-1', 'ТО-2', 'Ремонт', 'Диагностика', 'Замена масла']
        maintenance_statuses = ['Запланировано', 'В процессе', 'Выполнено']
        for i in range(50):
            ts_id = random.choice(vehicle_ids)
            date = datetime.now() + timedelta(days=random.randint(-60, 120))
            type_m = random.choice(maintenance_types)
            description = f"{type_m} для ТС {ts_id}"
            status = random.choice(maintenance_statuses)
            
            cursor.execute("""
                INSERT INTO maintenance (ts_id, date, type, description, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (ts_id, date, type_m, description, status, datetime.now()))
        
        conn.commit()
        print("✅ Database seeded successfully!")
        print("Added: 50 employees, 50 vehicles, 50 fines, 50 schedules, 50 maintenance records")
        
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    seed_database()
