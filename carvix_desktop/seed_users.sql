-- Тестовые данные для Carvix Desktop
-- Логины и пароль: 3 символа

-- Вставка ролей (если не существуют)
INSERT INTO rol (nazvanie) VALUES 
    ('Диспетчер'),
    ('Водитель'),
    ('Механик'),
    ('Администратор')
ON CONFLICT DO NOTHING;

-- Вставка подразделения (если не существует)
INSERT INTO podrazdelenie (nazvanie) VALUES 
    ('Главный офис')
ON CONFLICT DO NOTHING;

-- Удаление старых пользователей
DELETE FROM sotrudnik WHERE login IN ('dis', 'dri', 'mec', 'adm');

-- Вставка тестовых пользователей с логинами по 3 символа и паролем "123"
INSERT INTO sotrudnik (fio, login, parol_hash, rol_id, podrazdelenie_id, license_number, phone) 
VALUES 
    ('Диспетчер Иванов Иван Иванович', 'dis', '$2b$12$qoGGr1ErdUboKR1hoDWSVuOCVJf2qyhnKy..wkSc/0WXnZSjSL7Fe', 1, 1, '1234567890', '+79001234567'),
    ('Водитель Петров Петр Петрович', 'dri', '$2b$12$pe4b844b9OWzHchjo/5R0O943LMXl.8T./J35s.DBzQHV3ugcMgnS', 2, 1, '0987654321', '+79007654321'),
    ('Механик Сидоров Сидор Сидорович', 'mec', '$2b$12$Pq7g3ep85NsymlierjpSzO6OT.hsEv0yUxEbYqZniHNPgucCQxU1O', 3, 1, '5678901234', '+79009876543'),
    ('Администратор Козлов Константин Константинович', 'adm', '$2b$12$BCiczi3pNlZueB6tqlbSEeVLSr6gY.cL9wpmq5XXrGQ6CfBm1c1Du', 4, 1, '3456789012', '+79005432109');
