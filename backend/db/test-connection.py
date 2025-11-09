# test_db_connection.py
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()  # loads .env in the same folder

try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )
    cursor = conn.cursor()

    # 1) who am I?
    cursor.execute("SELECT CURRENT_USER(), USER();")
    print("CURRENT_USER(), USER():", cursor.fetchone())

    # 2) what users named thalia_app exist?
    cursor.execute("SELECT Host, User FROM mysql.user WHERE User = 'thalia_app';")
    rows = cursor.fetchall()
    print("mysql.user entries for thalia_app:")
    for r in rows:
        print(r)

    # 3) what grants does my current user have?
    cursor.execute("SHOW GRANTS FOR CURRENT_USER();")
    grants = cursor.fetchall()
    print("Grants for current user:")
    for g in grants:
        print(g[0])

    cursor.execute("SELECT 1;")
    result = cursor.fetchone()
    print("DB connection OK ✅, result:", result)
except Exception as e:
    print("DB connection FAILED ❌")
    print(e)
finally:
    try:
        cursor.close()
        conn.close()
    except:
        pass
