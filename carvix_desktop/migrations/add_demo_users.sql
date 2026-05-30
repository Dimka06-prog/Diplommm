-- Миграция: создание/обновление демонстрационных пользователей для всех ролей
-- Дата: 2026-05-27

-- Хеши паролей сгенерированы через bcrypt

INSERT INTO sotrudnik (fio, login, parol_hash, license_number, phone, rol_id, podrazdelenie_id)
VALUES
    ('Иванов Диспетчер', 'disp', '$2b$12$9V71etgJZqoou2OWenYGbO9cN5BSlaR1HnHawfjYgr9Trj2LL699e', 'DISP001', '+79990001122', 2, 1),
    ('Петров Механик', 'mech', '$2b$12$5DtT6OxLWxDmEg1bqEHC2BbfkbhN1JEyTcr.zzCq9wCl9jTTpdK', 'MECH001', '+79990003344', 3, 1),
    ('Сидоров Главный механик', 'chief', '$2b$12$nteiBCBRBfSsP6qkplIz7e2fo4BlA1gfOSdk2JsNMPaIzxiJtomn2', 'CHIEF001', '+79990005566', 4, 1),
    ('Кузнецов Аналитик', 'anal', '$2b$12$wQ0KRWnKleeh/c.BRMbA/.xHuh0YCRW5SYj5MiCQckTJQkVTLDQ1y', 'ANAL001', '+79990007788', 1, 1),
    ('Васильев Водитель', 'driver', '$2b$12$IfnsrjeZSXKIbaOFX48Pre0fY.CMYufwDqY4mU5c9wGbhbWSp9bqy', 'DRIV001', '+79990009900', 6, 1)
ON CONFLICT (login) DO UPDATE SET
    parol_hash = EXCLUDED.parol_hash,
    fio = EXCLUDED.fio,
    rol_id = EXCLUDED.rol_id,
    license_number = EXCLUDED.license_number,
    phone = EXCLUDED.phone,
    podrazdelenie_id = EXCLUDED.podrazdelenie_id;
