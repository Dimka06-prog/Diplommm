#!/usr/bin/env python3
"""
Migration script to add desktop application support to Render.com database
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def run_migration():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Read migration SQL
        with open('migrations/add_desktop_support.sql', 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✅ Migration completed successfully!")
        print("Added: app_settings, fines, work_schedule tables")
        print("Added: license_number, phone columns to sotrudnik")
        print("Added: assigned_driver_id, insurance_expiry, to_expiry to transportnoe_sredstvo")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_migration()
