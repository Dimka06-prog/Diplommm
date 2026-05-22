#!/usr/bin/env python3
"""
Rename role from Пользователь to Водитель
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def rename_user_role():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Update role name from Пользователь to Водитель
        cursor.execute("""
            UPDATE rol
            SET nazvanie = 'Водитель'
            WHERE nazvanie = 'Пользователь'
        """)
        
        updated = cursor.rowcount
        conn.commit()
        
        if updated > 0:
            print(f"✅ Role renamed: Пользователь -> Водитель ({updated} rows updated)")
        else:
            print("⚠️  No role named 'Пользователь' found")
        
        # Show all roles
        cursor.execute("SELECT id, nazvanie FROM rol ORDER BY id")
        roles = cursor.fetchall()
        print()
        print("Current roles:")
        for role in roles:
            print(f"  {role}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    rename_user_role()
