# backend/db/connection.py

import os
from dotenv import load_dotenv
import mysql.connector

# load .env
load_dotenv()

def get_db_connection():
    """
    create and return a MySQL connection
    """
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "3306"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "thalia"),  # keep same with run_schema.py
    )
    return conn
