import os
from dotenv import load_dotenv

load_dotenv()

# Support for DATABASE_URL (cloud databases like Neon, Supabase, etc.)
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Parse DATABASE_URL for individual components
    from urllib.parse import urlparse
    parsed = urlparse(DATABASE_URL)
    DB_CONFIG = {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/'),
        'user': parsed.username,
        'password': parsed.password,
        'database_url': DATABASE_URL
    }
else:
    # Individual environment variables (local PostgreSQL)
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'carvix'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', '')
    }

# SSL configuration (same as web app)
DB_SSL = os.getenv('PGSSL', 'false').lower() == 'true'

# Carvix design colors matching the web palette
COLORS = {
    'beige_50': '#FBF8F3',
    'beige_100': '#F5EFE3',
    'beige_200': '#ECE2CE',
    'beige_300': '#DCC9A8',
    'beige_400': '#C8AE82',
    'beige_500': '#A98B5C',
    'gray_50': '#F7F7F7',
    'gray_100': '#EFEFEE',
    'gray_200': '#E2E2E0',
    'gray_300': '#C9C8C4',
    'gray_400': '#9A9892',
    'gray_500': '#6F6D67',
    'gray_700': '#3F3D38',
    'gray_900': '#1C1B17',
    'white': '#FFFFFF',
    'danger': '#B23A3A',
    'success': '#4A7C59',
    'warning': '#e5a00d',
    'accent': '#1C1B17',
    'accent_soft': '#3F3D38'
}

# Role mappings
ROLES = {
    'dispatcher': {'id': 1, 'name': 'Диспетчер', 'name_en': 'dispatcher'},
    'driver': {'id': 2, 'name': 'Водитель', 'name_en': 'driver'},
    'mechanic': {'id': 3, 'name': 'Механик', 'name_en': 'mechanic'},
    'admin': {'id': 4, 'name': 'Администратор', 'name_en': 'admin'}
}

APP_NAME = 'Carvix — Учет водителей и ТС'
APP_VERSION = '1.0.0'
