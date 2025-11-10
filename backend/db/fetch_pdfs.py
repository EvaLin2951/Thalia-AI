from connection import get_db_connection

def fetch_pdf_texts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_name, content, title, authors, journal, year, doi FROM pdf_documents")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"file_name": r[0], "content": r[1], "title": r[2], "authors": r[3], "journal": r[4], "year": r[5], "doi": r[6]} for r in rows]


if __name__ == "__main__":
    docs = fetch_pdf_texts()
    for doc in docs:
        print(f"\n {doc['file_name']}\n{'-'*50}\n{doc['content'][:500]}...\n")
        print(f"Metadata: Title={doc['title']}, Authors={doc['authors']}, Journal={doc['journal']}, Year={doc['year']}, DOI={doc['doi']}\n")