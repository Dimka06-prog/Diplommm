-- Дополнительные таблицы для desktop-приложения Carvix
-- Добавляются к существующей схеме базы данных

-- Таблица штрафов (если отсутствует)
CREATE TABLE IF NOT EXISTS fines (
    id SERIAL PRIMARY KEY,
    ts_id INT REFERENCES transportnoe_sredstvo(id),
    date DATE NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'Не оплачен',
    postanovlenie_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Таблица графика работы (если отсутствует)
CREATE TABLE IF NOT EXISTS work_schedule (
    id SERIAL PRIMARY KEY,
    driver_id INT REFERENCES sotrudnik(id),
    ts_id INT REFERENCES transportnoe_sredstvo(id),
    date DATE NOT NULL,
    shift_start VARCHAR(10) DEFAULT '08:00',
    shift_end VARCHAR(10) DEFAULT '20:00',
    status VARCHAR(50) DEFAULT 'Запланирована',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Добавление недостающих полей в таблицу sotrudnik (если отсутствуют)
ALTER TABLE sotrudnik ADD COLUMN IF NOT EXISTS license_number VARCHAR(100);
ALTER TABLE sotrudnik ADD COLUMN IF NOT EXISTS license_expiry DATE;
ALTER TABLE sotrudnik ADD COLUMN IF NOT EXISTS phone VARCHAR(50);

-- Добавление недостающих полей в таблицу transportnoe_sredstvo (если отсутствуют)
ALTER TABLE transportnoe_sredstvo ADD COLUMN IF NOT EXISTS vin VARCHAR(50);
ALTER TABLE transportnoe_sredstvo ADD COLUMN IF NOT EXISTS assigned_driver_id INT REFERENCES sotrudnik(id);
ALTER TABLE transportnoe_sredstvo ADD COLUMN IF NOT EXISTS insurance_expiry DATE;
ALTER TABLE transportnoe_sredstvo ADD COLUMN IF NOT EXISTS to_expiry DATE;

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_fines_ts_id ON fines(ts_id);
CREATE INDEX IF NOT EXISTS idx_fines_date ON fines(date);
CREATE INDEX IF NOT EXISTS idx_work_schedule_driver_id ON work_schedule(driver_id);
CREATE INDEX IF NOT EXISTS idx_work_schedule_ts_id ON work_schedule(ts_id);
CREATE INDEX IF NOT EXISTS idx_work_schedule_date ON work_schedule(date);
