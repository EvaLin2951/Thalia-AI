# backend/db/run_schema.py
import os
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

def main():
    # schema.sql is in the same folder as this file
    schema_path = Path(__file__).with_name("schema.sql")
    if not schema_path.exists():
        raise FileNotFoundError(f"Could not find schema file at {schema_path}")

    with schema_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "3306"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "thalia"),  # make sure .env has this
    )
    cur = conn.cursor()

    stmt_buf = []

    def should_skip_statement(sql_upper: str) -> bool:
        return (
            sql_upper.startswith("DELIMITER")
            or sql_upper.startswith("SET GLOBAL")
            or sql_upper.startswith("DROP EVENT")
            or sql_upper.startswith("CREATE EVENT")
            or sql_upper.startswith("CREATE DATABASE")
            or sql_upper.startswith("USE ")
        )

    for line in lines:
        stripped = line.strip()

        # skip empty lines
        if not stripped:
            continue

        # skip comments
        if stripped.startswith("--"):
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("/*"):
            continue
        # skip lines that are just dashes like "------"
        if set(stripped) == {"-"}:
            continue

        stmt_buf.append(line)

        # if this line ends a statement
        if stripped.endswith(";"):
            full_stmt = "".join(stmt_buf).strip()
            stmt_buf = []

            # drop the trailing ;
            if full_stmt.endswith(";"):
                full_stmt = full_stmt[:-1].strip()

            upper = full_stmt.upper()
            if should_skip_statement(upper):
                continue

            # execute the good statement
            cur.execute(full_stmt)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ schema.sql applied")

if __name__ == "__main__":
    main()
