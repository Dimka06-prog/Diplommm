-- Migration script to add desktop application support to Render.com database
-- Execute this script against the Render.com database

-- Add missing columns to sotrudnik table
ALTER TABLE sotrudnik ADD COLUMN IF NOT EXISTS license_number VARCHAR(20);
ALTER TABLE sotrudnik ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
ALTER TABLE sotrudnik ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add missing columns to transportnoe_sredstvo table
ALTER TABLE transportnoe_sredstvo ADD COLUMN IF NOT EXISTS vin VARCHAR(17);
ALTER TABLE transportnoe_sredstvo ADD COLUMN IF NOT EXISTS assigned_driver_id INTEGER;

-- Add foreign key constraint (skip if already exists using DO block)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_transportnoe_sredstvo_assigned_driver'
    ) THEN
        ALTER TABLE transportnoe_sredstvo 
        ADD CONSTRAINT fk_transportnoe_sredstvo_assigned_driver 
        FOREIGN KEY (assigned_driver_id) REFERENCES sotrudnik(id);
    END IF;
END $$;

ALTER TABLE transportnoe_sredstvo ADD COLUMN IF NOT EXISTS insurance_expiry DATE;
ALTER TABLE transportnoe_sredstvo ADD COLUMN IF NOT EXISTS to_expiry DATE;
ALTER TABLE transportnoe_sredstvo ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add model_id column if it doesn't exist and make it nullable
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'transportnoe_sredstvo' AND column_name = 'model_id'
    ) THEN
        ALTER TABLE transportnoe_sredstvo ADD COLUMN model_id INTEGER;
    END IF;
END $$;

-- Create app_settings table
CREATE TABLE IF NOT EXISTS app_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_app_settings_key ON app_settings(key);

-- Insert default settings
INSERT INTO app_settings (key, value) 
VALUES 
    ('session_timeout_minutes', '30'),
    ('default_language', 'ru')
ON CONFLICT (key) DO NOTHING;

-- Create fines table
CREATE TABLE IF NOT EXISTS fines (
    id SERIAL PRIMARY KEY,
    ts_id INTEGER REFERENCES transportnoe_sredstvo(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'Не оплачен',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fines_ts_id ON fines(ts_id);
CREATE INDEX IF NOT EXISTS idx_fines_date ON fines(date);
CREATE INDEX IF NOT EXISTS idx_fines_status ON fines(status);

-- Add postanovlenie_number column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'fines' AND column_name = 'postanovlenie_number'
    ) THEN
        ALTER TABLE fines ADD COLUMN postanovlenie_number VARCHAR(50);
    END IF;
END $$;

-- Create work_schedule table
CREATE TABLE IF NOT EXISTS work_schedule (
    id SERIAL PRIMARY KEY,
    ts_id INTEGER REFERENCES transportnoe_sredstvo(id) ON DELETE CASCADE,
    driver_id INTEGER REFERENCES sotrudnik(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    shift_start TIME,
    shift_end TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_work_schedule_ts_id ON work_schedule(ts_id);
CREATE INDEX IF NOT EXISTS idx_work_schedule_driver_id ON work_schedule(driver_id);
CREATE INDEX IF NOT EXISTS idx_work_schedule_date ON work_schedule(date);

-- Add status column to work_schedule if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'work_schedule' AND column_name = 'status'
    ) THEN
        ALTER TABLE work_schedule ADD COLUMN status VARCHAR(50) DEFAULT 'Запланировано';
    END IF;
END $$;

-- Create maintenance table
CREATE TABLE IF NOT EXISTS maintenance (
    id SERIAL PRIMARY KEY,
    ts_id INTEGER REFERENCES transportnoe_sredstvo(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'Запланировано',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_maintenance_ts_id ON maintenance(ts_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_date ON maintenance(date);
CREATE INDEX IF NOT EXISTS idx_maintenance_type ON maintenance(type);

-- Add trigger to update updated_at timestamp for app_settings
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop trigger if exists, then create it
DROP TRIGGER IF EXISTS update_app_settings_updated_at ON app_settings;
CREATE TRIGGER update_app_settings_updated_at BEFORE UPDATE ON app_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
