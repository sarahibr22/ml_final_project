import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_conn():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "med_db"),
        user=os.getenv("POSTGRES_USER", "med_user"),
        password=os.getenv("POSTGRES_PASSWORD", "med_pass"),
        host=os.getenv("POSTGRES_HOST", "database"),
        port=os.getenv("POSTGRES_PORT", "5432")
    )
