#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/dmitrirodkin/PycharmProjects/Diplom_Rodkin/carvix_desktop')

from src.database import Database

def fix():
    driver = Database.execute_query('SELECT id FROM sotrudnik WHERE login = %s', ('driver',))
    if not driver:
        print("[ERROR] Driver not found")
        return
    driver_id = driver[0]['id']

    vehicles = Database.execute_query(
        'SELECT id, gos_nomer FROM transportnoe_sredstvo WHERE assigned_driver_id = %s ORDER BY id',
        (driver_id,)
    )
    print(f"[INFO] Driver has {len(vehicles)} vehicle(s)")
    for v in vehicles:
        print(f"  - {v['gos_nomer']}")

    if len(vehicles) > 1:
        keep_id = vehicles[0]['id']
        keep_gos = vehicles[0]['gos_nomer']
        release_ids = [v['id'] for v in vehicles[1:]]
        for vid in release_ids:
            Database.execute_query(
                'UPDATE transportnoe_sredstvo SET assigned_driver_id = NULL WHERE id = %s',
                (vid,), fetch=False
            )
        print(f"[OK] Kept {keep_gos} for driver, released {len(release_ids)} vehicles")
    else:
        print("[OK] Driver already has 1 vehicle")

if __name__ == '__main__':
    fix()
