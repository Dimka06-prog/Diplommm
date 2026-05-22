#!/usr/bin/env python3
"""
Get user credentials for login
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def get_user_credentials():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.login, s.parol_hash, r.nazvanie
            FROM sotrudnik s
            JOIN rol r ON s.rol_id = r.id
            ORDER BY s.id
        """)
        
        users = cursor.fetchall()
        
        print("=== ЛОГИНЫ ДЛЯ ВХОДА ===")
        print("Все пользователи имеют пароль: password123")
        print()
        
        # Group by role
        roles = {}
        for login, _, role in users:
            if role not in roles:
                roles[role] = []
            roles[role].append(login)
        
        for role, logins in roles.items():
            print(f"Роль: {role}")
            for i, login in enumerate(logins[:5]):  # Show first 5 per role
                print(f"  Логин: {login}")
            if len(logins) > 5:
                print(f"  ... и еще {len(logins) - 5} пользователей")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.close()

if __name__ == "__main__":
    get_user_credentials()
