import os
from pathlib import Path
from sqlite3 import connect, Connection, Cursor
from app.config import DB_PATH, DB_DIR

# Global variables for the database connection and cursor, along with an initialization flag
conn: Connection
curs: Cursor
db_initialized: bool = False

def get_db(name: str | None = None):
    global conn, curs, db_initialized

    # Check if the connection is already initialized and if reset is not requested
    if db_initialized:
        return conn, curs

    # Determine database path - use centralized config
    if not name:
        db_path = str(DB_PATH)
    else:
        db_path = name

    # Ensure database directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)

    # Establish new connection and cursor
    conn = connect(db_path, check_same_thread=False)
    curs = conn.cursor()

    # Enable foreign key support and mark initialization
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = normal")
    db_initialized = True

    return conn, curs

# Initialize if not already done
if not db_initialized:
    conn, curs = get_db()

