import os
from dotenv import load_dotenv
import mysql.connector

#loads the environment variables from a .env file
load_dotenv()

def get_db_connection():
    """Establishes and returns a connection to the database using environment variables."""
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return connection
