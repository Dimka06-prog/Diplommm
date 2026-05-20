from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

@dataclass
class Employee:
    id: int
    fio: str
    login: str
    rol_id: int
    rol_name: str
    podrazdelenie_id: int
    podrazdelenie_name: str
    license_number: Optional[str] = None
    license_expiry: Optional[date] = None
    phone: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            fio=data['fio'],
            login=data['login'],
            rol_id=data['rol_id'],
            rol_name=data.get('rol_name', ''),
            podrazdelenie_id=data['podrazdelenie_id'],
            podrazdelenie_name=data.get('podrazdelenie_name', ''),
            license_number=data.get('license_number'),
            license_expiry=data.get('license_expiry'),
            phone=data.get('phone')
        )

@dataclass
class Vehicle:
    id: int
    gos_nomer: str
    invent_nomer: str
    marka_name: str
    model_name: str
    model_id: int
    podrazdelenie_id: int
    podrazdelenie_name: str
    probeg: int
    data_vypuska: Optional[date]
    tekuschee_sostoyanie: str
    vin: Optional[str] = None
    assigned_driver_id: Optional[int] = None
    assigned_driver_fio: Optional[str] = None
    insurance_expiry: Optional[date] = None
    to_expiry: Optional[date] = None
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            gos_nomer=data['gos_nomer'],
            invent_nomer=data['invent_nomer'],
            marka_name=data.get('marka_name', ''),
            model_name=data.get('model_name', ''),
            model_id=data['model_id'],
            podrazdelenie_id=data['podrazdelenie_id'],
            podrazdelenie_name=data.get('podrazdelenie_name', ''),
            probeg=data.get('probeg', 0),
            data_vypuska=data.get('data_vypuska'),
            tekuschee_sostoyanie=data.get('tekuschee_sostoyanie', 'Активное'),
            vin=data.get('vin'),
            assigned_driver_id=data.get('assigned_driver_id'),
            assigned_driver_fio=data.get('assigned_driver_fio'),
            insurance_expiry=data.get('insurance_expiry'),
            to_expiry=data.get('to_expiry')
        )

@dataclass
class Fine:
    id: int
    ts_id: int
    gos_nomer: str
    amount: float
    date: date
    description: str
    status: str
    postanovlenie_number: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            ts_id=data['ts_id'],
            gos_nomer=data.get('gos_nomer', ''),
            amount=data['amount'],
            date=data['date'],
            description=data.get('description', ''),
            status=data.get('status', 'Не оплачен'),
            postanovlenie_number=data.get('postanovlenie_number')
        )

@dataclass
class Maintenance:
    id: int
    ts_id: int
    gos_nomer: str
    to_date: date
    to_type: str
    result: str
    next_to_date: Optional[date]
    cost: float
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            ts_id=data['ts_id'],
            gos_nomer=data.get('gos_nomer', ''),
            to_date=data['to_date'],
            to_type=data.get('to_type', 'ТО-1'),
            result=data.get('result', 'Пройден'),
            next_to_date=data.get('next_to_date'),
            cost=data.get('cost', 0.0)
        )

@dataclass
class WorkSchedule:
    id: int
    driver_id: int
    driver_fio: str
    ts_id: int
    gos_nomer: str
    date: date
    shift_start: str
    shift_end: str
    status: str
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            driver_id=data['driver_id'],
            driver_fio=data.get('driver_fio', ''),
            ts_id=data['ts_id'],
            gos_nomer=data.get('gos_nomer', ''),
            date=data['date'],
            shift_start=data.get('shift_start', '08:00'),
            shift_end=data.get('shift_end', '20:00'),
            status=data.get('status', 'Запланирована')
        )
