#!/usr/bin/env python3
"""
Clean up roles to restore to working state
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def clean_roles():
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
        
        # Update users with role_id = 7 to role_id = 6 (Пользователь)
        print("Updating users with role_id = 7 to role_id = 6...")
        cursor.execute("""
            UPDATE sotrudnik SET rol_id = 6 WHERE rol_id = 7
        """)
        updated = cursor.rowcount
        if updated > 0:
            print(f"  Updated {updated} users from role 7 to role 6")
        
        # Delete role 7 (Водитель)
        print("Deleting role 7 (Водитель)...")
        cursor.execute("DELETE FROM rol WHERE id = 7")
        print("  Deleted role 7")
        
        # Restore original roles (1-6)
        original_roles = {
            1: 'Аналитик',
            2: 'Диспетчер',
            3: 'Механик',
            4: 'Главный механик',
            5: 'Директор',
            6: 'Пользователь'
        }
        
        print("Restoring original roles (1-6)...")
        for role_id, role_name in original_roles.items():
            cursor.execute("""
                INSERT INTO rol (id, nazvanie)
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE SET
                nazvanie = EXCLUDED.nazvanie
            """, (role_id, role_name))
            print(f"  Set role {role_id}: {role_name}")
        
        conn.commit()
        print("✅ Roles cleaned successfully!")
        
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
    clean_roles()
