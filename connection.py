import psycopg2
from psycopg2.extras import RealDictCursor


DATABASE_CONFIG = {
    "dbname": "spatial_data",
    "user": "",
    "password": "your_password",
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)
