-- Таблица настроек приложения
CREATE TABLE IF NOT EXISTS app_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индекс для быстрого поиска по ключу
CREATE INDEX IF NOT EXISTS idx_app_settings_key ON app_settings(key);

-- Вставка настроек по умолчанию
INSERT INTO app_settings (key, value) VALUES
    ('company_name', 'Carvix'),
    ('maintenance_reminder_days', '30'),
    ('insurance_reminder_days', '30'),
    ('auto_sync_gibdd', 'false'),
    ('session_timeout_minutes', '60')
ON CONFLICT (key) DO NOTHING;
