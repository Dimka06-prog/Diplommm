#!/usr/bin/env python3
"""
Create simple 3-character logins and passwords
"""

import psycopg2
import random
import os
from dotenv import load_dotenv
import bcrypt
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_simple_users():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Get role IDs
        cursor.execute("SELECT id, nazvanie FROM rol")
        roles = {row[1]: row[0] for row in cursor.fetchall()}
        
        # Get department ID
        cursor.execute("SELECT id FROM podrazdelenie LIMIT 1")
        dept = cursor.fetchone()
        dept_id = dept[0] if dept else None
        
        # Delete existing users created by seed script
        cursor.execute("DELETE FROM sotrudnik WHERE login LIKE 'user_%'")
        conn.commit()
        print("Deleted existing seed users")
        
        # Create simple users for each role
        simple_logins = ['abc', 'def', 'ghi', 'jkl', 'mno', 'pqr', 'stu']
        password = hash_password("123")

        # Create users for the actual roles in the database
        roles_list = ['Аналитик', 'Диспетчер', 'Механик', 'Главный механик', 'Директор', 'Пользователь', 'Водитель']
        
        print("Creating simple users...")
        for i, role_name in enumerate(roles_list):
            if role_name in roles:
                login = simple_logins[i]
                fio = f"Пользователь {role_name}"
                
                cursor.execute("""
                    INSERT INTO sotrudnik (fio, login, parol_hash, rol_id, podrazdelenie_id, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (login) DO UPDATE SET
                    fio = EXCLUDED.fio,
                    parol_hash = EXCLUDED.parol_hash,
                    rol_id = EXCLUDED.rol_id
                """, (fio, login, password, roles[role_name], dept_id, datetime.now()))
                
                print(f"Created: {login} (role: {role_name})")
        
        conn.commit()
        print("✅ Simple users created successfully!")
        print()
        print("=== ЛОГИНЫ ДЛЯ ВХОДА ===")
        print("Пароль для всех: 123")
        print()
        for i, role_name in enumerate(roles_list):
            if role_name in roles:
                print(f"{role_name}: {simple_logins[i]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_simple_users()
