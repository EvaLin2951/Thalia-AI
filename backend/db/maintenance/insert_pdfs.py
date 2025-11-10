import os
# make sure we get the real PyMuPDF
try:
    import fitz  # this should be PyMuPDF
    if not hasattr(fitz, "open"):
        raise ImportError
except ImportError:
    # fallback if something shadows it
    import pymupdf as fitz # PyMuPDF
from datetime import datetime
from backend.db.connection import get_db_connection

def extract_metadata_from_pdf(file_path):
    doc = fitz.open(file_path)
    metadata = doc.metadata or {}

    raw_date = metadata.get("creationDate")  # e.g. "D:20241109..."
    year = None
    if raw_date and len(raw_date) >= 6:
        # D:YYYY...
        year_part = raw_date[2:6]
        if year_part.isdigit():
            year = int(year_part)


    return {
        "title": metadata.get("title", "") or "",
        "authors": metadata.get("author", "") or "", 
        "year": year,
        "journal": metadata.get("subject", "") or "",
        "doi": metadata.get("keywords", "") or ""
    }

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    return "\n".join(page.get_text() for page in doc)

def insert_pdf(file_path):
    text = extract_text_from_pdf(file_path)
    file_name = os.path.basename(file_path)
    meta = extract_metadata_from_pdf(file_path)

    title = (meta.get("title") or "")[:500]
    journal = (meta.get("journal") or "")[:500]
    author = (meta.get("author") or "")[:255]


    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM pdf_documents WHERE file_name = %s", (file_name,))
    (count,) = cursor.fetchone()

    if count>0:
        print(f"Skipping {file_name} — already in database.")
    else:
        cursor.execute(
            """
            INSERT INTO pdf_documents
            (file_name, title, authors, journal, year, doi, content, file_path, last_indexed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                file_name,
                title,  # fallback to filename
                author,
                journal,
                meta["year"],
                meta["doi"],
                text,
                file_path,
                datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        print(f"Inserted {file_name} into database.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    pdf_folder = os.path.join(os.path.dirname(__file__), "..", "pdfs")
    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):
            insert_pdf(os.path.join(pdf_folder, file))
