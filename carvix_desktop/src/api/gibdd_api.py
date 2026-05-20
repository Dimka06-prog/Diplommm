import requests
from datetime import date
from typing import List, Dict, Optional

class GibddAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.gibdd.ru"
        
    def check_fines_by_vin(self, vin: str) -> List[Dict]:
        try:
            return []
        except:
            return []
    
    def check_fines_by_gos_number(self, gos_nomer: str) -> List[Dict]:
        try:
            return []
        except:
            return []
    
    def sync_fines_to_db(self, db_connection, vehicle_id: int, gos_nomer: str) -> int:
        fines = self.check_fines_by_gos_number(gos_nomer)
        synced_count = 0
        return synced_count

class NotificationSystem:
    @staticmethod
    def check_maintenance_due(db_connection, days_before: int = 30) -> List[Dict]:
        try:
            query = """SELECT id, gos_nomer, to_expiry FROM transportnoe_sredstvo
                       WHERE to_expiry IS NOT NULL
                       AND to_expiry <= CURRENT_DATE + INTERVAL '%s days'""" % days_before
            return db_connection.execute_query(query)
        except:
            return []
    
    @staticmethod
    def check_insurance_due(db_connection, days_before: int = 30) -> List[Dict]:
        try:
            query = """SELECT id, gos_nomer, insurance_expiry FROM transportnoe_sredstvo
                       WHERE insurance_expiry IS NOT NULL
                       AND insurance_expiry <= CURRENT_DATE + INTERVAL '%s days'""" % days_before
            return db_connection.execute_query(query)
        except:
            return []
