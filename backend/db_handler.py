import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def create_jobs_table():
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id         VARCHAR(36) PRIMARY KEY,
                    filename       TEXT NOT NULL,
                    status         TEXT NOT NULL DEFAULT 'queued',
                    chunks_created INTEGER,
                    s3_key         TEXT,
                    error          TEXT,
                    created_at     TIMESTAMP DEFAULT NOW()
                )
            """
            )
    conn.close()


def create_job(job_id, filename, status="pending"):
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO jobs (job_id, filename, status) VALUES (%s, %s, %s)",
                (job_id, filename, status),
            )
    conn.close()


def update_job(job_id, **kwargs):
    # Builds SET clause from whatever fields are passed — avoids a separate function per field
    fields = ", ".join(f"{k} = %s" for k in kwargs)
    values = list(kwargs.values()) + [job_id]
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE jobs SET {fields} WHERE job_id = %s", values)
    conn.close()


def get_job(job_id):
    conn = get_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
        row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
