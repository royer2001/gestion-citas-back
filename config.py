import os

# para entornos de producción - pip install psycopg2 actual con -binary

MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'cursorclass': 'DictCursor'
}

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

API_PERU_DEV_TOKEN = os.getenv('API_PERU_DEV_TOKEN')

SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')

SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
