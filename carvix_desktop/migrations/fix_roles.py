#!/usr/bin/env python3
"""
Fix roles to match desktop application expectations
Desktop app expects:
- dispatcher (id: 1) = Диспетчер
- driver (id: 2) = Водитель
- mechanic (id: 3) = Механик
- admin (id: 4) = Администратор
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def fix_roles():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Get current roles
        cursor.execute("SELECT id, nazvanie FROM rol ORDER BY id")
        current_roles = cursor.fetchall()
        print("Current roles:")
        for role in current_roles:
            print(f"  {role}")
        print()
        
        # Update or create roles to match desktop app expectations
        expected_roles = {
            1: 'Диспетчер',
            2: 'Водитель',
            3: 'Механик',
            4: 'Администратор'
        }

        # First, update sotrudnik records to use new role mapping
        # Map old role IDs to new role IDs
        role_mapping = {
            1: 1,  # Аналитик -> Диспетчер
            2: 1,  # Диспетчер -> Диспетчер
            3: 3,  # Механик -> Механик
            4: 3,  # Главный механик -> Механик
            5: 4,  # Директор -> Администратор
            6: 2   # Пользователь -> Водитель
        }

        print("Updating sotrudnik role references...")
        for old_role_id, new_role_id in role_mapping.items():
            cursor.execute("""
                UPDATE sotrudnik SET rol_id = %s WHERE rol_id = %s
            """, (new_role_id, old_role_id))
            updated = cursor.rowcount
            if updated > 0:
                print(f"  Updated {updated} users from role {old_role_id} to {new_role_id}")

        print("Updating roles to match desktop app...")
        for role_id, role_name in expected_roles.items():
            cursor.execute("""
                INSERT INTO rol (id, nazvanie)
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE SET
                nazvanie = EXCLUDED.nazvanie
            """, (role_id, role_name))
            print(f"  Set role {role_id}: {role_name}")

        # Delete extra roles (ids > 4)
        cursor.execute("DELETE FROM rol WHERE id > 4")
        print("  Deleted extra roles")
        
        conn.commit()
        print("✅ Roles fixed successfully!")
        
        # Show final roles
        cursor.execute("SELECT id, nazvanie FROM rol ORDER BY id")
        final_roles = cursor.fetchall()
        print()
        print("Final roles:")
        for role in final_roles:
            print(f"  {role}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_roles()
