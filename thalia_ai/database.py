"""
Database module for Thalia AI
Simple MySQL database operations for demonstration purposes
"""

import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file in current directory
# override=True ensures .env file values take precedence over system env vars
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

def get_db_connection():
    """Create and return MySQL database connection"""
    host = os.getenv('DB_HOST', '34.171.72.225')
    port = int(os.getenv('DB_PORT', '3306'))
    user = os.getenv('DB_USER', 'thalia_app')
    password = os.getenv('DB_PASSWORD', 'ThaliaAI4Good!')
    db = os.getenv('DB_NAME', 'thalia')

    # Uncomment below line for connection debugging
    # print(f"Connecting to: {host}:{port} with user: {user}, db: {db}")

    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db
    )

def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            age INT,
            baseline_completed BOOLEAN DEFAULT FALSE,
            baseline_date VARCHAR(20),
            baseline_total_score INT,
            baseline_severity VARCHAR(20),
            baseline_psychological_score INT,
            baseline_somatic_score INT,
            baseline_urogenital_score INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Symptom logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS symptom_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            date VARCHAR(20) NOT NULL,
            symptom_id VARCHAR(50) NOT NULL,
            symptom_name VARCHAR(100),
            type VARCHAR(20) NOT NULL,
            d_evt_count INT,
            d_evt_sev_max INT,
            d_sev INT,
            w_anchor_sev INT,
            deleted BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE KEY unique_log (user_id, date, symptom_id)
        )
    """)
    
    # MRS assessments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mrs_assessments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            date VARCHAR(20) NOT NULL,
            total_score INT NOT NULL,
            severity VARCHAR(20),
            psychological_score INT,
            somatic_score INT,
            urogenital_score INT,
            answers JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database tables created successfully")

# User operations
def get_user(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_all_users():
    """Get all users"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

def create_user(user_data):
    """Create or update user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO users (id, name, email, age, baseline_completed, baseline_date, 
                          baseline_total_score, baseline_severity, baseline_psychological_score,
                          baseline_somatic_score, baseline_urogenital_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            email = VALUES(email),
            age = VALUES(age),
            baseline_completed = VALUES(baseline_completed),
            baseline_date = VALUES(baseline_date),
            baseline_total_score = VALUES(baseline_total_score),
            baseline_severity = VALUES(baseline_severity),
            baseline_psychological_score = VALUES(baseline_psychological_score),
            baseline_somatic_score = VALUES(baseline_somatic_score),
            baseline_urogenital_score = VALUES(baseline_urogenital_score)
    """, (
        user_data['id'],
        user_data['name'],
        user_data['email'],
        user_data.get('age'),
        user_data.get('baseline_completed', False),
        user_data.get('baseline_date'),
        user_data.get('baseline_total_score'),
        user_data.get('baseline_severity'),
        user_data.get('baseline_psychological_score'),
        user_data.get('baseline_somatic_score'),
        user_data.get('baseline_urogenital_score')
    ))
    
    conn.commit()
    cursor.close()
    conn.close()

# Symptom log operations
def get_logs(user_id, start_date=None, end_date=None):
    """Get symptom logs for user"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT * FROM symptom_logs WHERE user_id = %s AND deleted = FALSE"
    params = [user_id]
    
    if start_date and end_date:
        query += " AND date BETWEEN %s AND %s"
        params.extend([start_date, end_date])
    
    query += " ORDER BY date DESC"
    
    cursor.execute(query, params)
    logs = cursor.fetchall()
    cursor.close()
    conn.close()
    return logs

def save_log(log_data):
    """Save or update symptom log"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO symptom_logs (user_id, date, symptom_id, symptom_name, type,
                                  d_evt_count, d_evt_sev_max, d_sev, w_anchor_sev, deleted)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            symptom_name = VALUES(symptom_name),
            type = VALUES(type),
            d_evt_count = VALUES(d_evt_count),
            d_evt_sev_max = VALUES(d_evt_sev_max),
            d_sev = VALUES(d_sev),
            w_anchor_sev = VALUES(w_anchor_sev),
            deleted = VALUES(deleted)
    """, (
        log_data['user_id'],
        log_data['date'],
        log_data['symptom_id'],
        log_data.get('symptom_name'),
        log_data['type'],
        log_data.get('d_evt_count'),
        log_data.get('d_evt_sev_max'),
        log_data.get('d_sev'),
        log_data.get('w_anchor_sev'),
        log_data.get('deleted', False)
    ))
    
    conn.commit()
    cursor.close()
    conn.close()

def delete_log(user_id, date, symptom_id):
    """Mark log as deleted"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE symptom_logs 
        SET deleted = TRUE 
        WHERE user_id = %s AND date = %s AND symptom_id = %s
    """, (user_id, date, symptom_id))
    
    conn.commit()
    cursor.close()
    conn.close()

# MRS assessment operations
def get_mrs_history(user_id):
    """Get MRS assessment history for user"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM mrs_assessments 
        WHERE user_id = %s 
        ORDER BY date DESC
    """, (user_id,))
    
    assessments = cursor.fetchall()
    cursor.close()
    conn.close()
    return assessments

def save_mrs_assessment(assessment_data):
    """Save MRS assessment"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    import json
    
    cursor.execute("""
        INSERT INTO mrs_assessments (user_id, date, total_score, severity,
                                     psychological_score, somatic_score, urogenital_score, answers)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        assessment_data['user_id'],
        assessment_data['date'],
        assessment_data['total_score'],
        assessment_data.get('severity'),
        assessment_data.get('psychological_score'),
        assessment_data.get('somatic_score'),
        assessment_data.get('urogenital_score'),
        json.dumps(assessment_data.get('answers', {}))
    ))
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    # Initialize database when run directly
    init_database()
