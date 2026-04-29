import sqlite3

DB_NAME = "goat.db"

def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS goat_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goat_id TEXT,
        temperature REAL,
        movement INTEGER,
        feed INTEGER,
        timestamp TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goat_id TEXT,
        alert TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()
