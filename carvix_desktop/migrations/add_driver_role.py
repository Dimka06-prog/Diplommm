#!/usr/bin/env python3
"""
Add role 7 (Водитель) to database
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def add_driver_role():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Add role 7 (Водитель)
        cursor.execute("""
            INSERT INTO rol (id, nazvanie)
            VALUES (7, 'Водитель')
            ON CONFLICT (id) DO UPDATE SET
            nazvanie = EXCLUDED.nazvanie
        """)
        
        conn.commit()
        print("✅ Role 7 (Водитель) added successfully!")
        
        # Show all roles
        cursor.execute("SELECT id, nazvanie FROM rol ORDER BY id")
        roles = cursor.fetchall()
        print()
        print("All roles:")
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
    add_driver_role()
