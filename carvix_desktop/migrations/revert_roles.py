#!/usr/bin/env python3
"""
Revert roles back to original state to fix website
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def revert_roles():
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
        
        # Revert to original roles
        original_roles = {
            1: 'Аналитик',
            2: 'Диспетчер',
            3: 'Механик',
            4: 'Главный механик',
            5: 'Директор',
            6: 'Пользователь'
        }

        # First restore all original roles (1-6) so foreign key constraints work
        print("Restoring original roles (1-6)...")
        for role_id, role_name in original_roles.items():
            cursor.execute("""
                INSERT INTO rol (id, nazvanie)
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE SET
                nazvanie = EXCLUDED.nazvanie
            """, (role_id, role_name))
            print(f"  Set role {role_id}: {role_name}")

        # Then revert sotrudnik role references back to original mapping
        # Map current roles back to original roles
        role_mapping = {
            1: 2,  # Диспетчер -> Диспетчер (was 2)
            2: 6,  # Водитель -> Пользователь (was 6)
            3: 3,  # Механик -> Механик (was 3)
            4: 5   # Администратор -> Директор (was 5)
        }

        print("Reverting sotrudnik role references...")
        for new_role_id, old_role_id in role_mapping.items():
            cursor.execute("""
                UPDATE sotrudnik SET rol_id = %s WHERE rol_id = %s
            """, (old_role_id, new_role_id))
            updated = cursor.rowcount
            if updated > 0:
                print(f"  Updated {updated} users from role {new_role_id} to {old_role_id}")

        # Delete extra roles (ids > 6)
        print("Deleting extra roles (ids > 6)...")
        cursor.execute("DELETE FROM rol WHERE id > 6")
        print("  Deleted extra roles")
        
        conn.commit()
        print("✅ Roles reverted successfully!")
        
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
    revert_roles()
