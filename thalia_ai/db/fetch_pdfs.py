"""
Fetch PDF documents from MySQL database
"""
import mysql.connector
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

def get_db_connection():
    """Create database connection"""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', '34.171.72.225'),
        port=int(os.getenv('DB_PORT', '3306')),
        user=os.getenv('DB_USER', 'thalia_app'),
        password=os.getenv('DB_PASSWORD', 'ThaliaAI4Good!'),
        database=os.getenv('DB_NAME', 'thalia')
    )

def fetch_pdf_texts():
    """
    Fetch PDF documents from database
    Returns list of dicts with 'file_name' and 'content' keys
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Query to get PDF documents
        # Assuming table name is 'pdf_documents' with columns: file_name, content
        query = "SELECT file_name, content FROM pdf_documents"

        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        print(f"✅ Fetched {len(results)} PDF documents from database")
        return results

    except mysql.connector.Error as e:
        if e.errno == 1146:  # Table doesn't exist
            print(f"⚠️  Table 'pdf_documents' does not exist in database")
            print(f"   Returning empty list - RAG will be unavailable")
            return []
        else:
            print(f"❌ Database error: {e}")
            raise

if __name__ == '__main__':
    # Test function
    docs = fetch_pdf_texts()
    print(f"Found {len(docs)} documents")
    if docs:
        print(f"First document: {docs[0]['file_name']}")
