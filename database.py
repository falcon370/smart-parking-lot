import sqlite3

DB_NAME = "parking.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the three tables if they don't exist yet."""
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT UNIQUE NOT NULL,
            vehicle_type TEXT NOT NULL,
            owner        TEXT
        );
        CREATE TABLE IF NOT EXISTS parking_slots (
            slot_id     INTEGER PRIMARY KEY,
            slot_type   TEXT NOT NULL,
            is_occupied INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL REFERENCES vehicles(vehicle_id),
            slot_id    INTEGER NOT NULL REFERENCES parking_slots(slot_id),
            entry_time TEXT NOT NULL,
            exit_time  TEXT,
            amount     REAL
        );
        """)
