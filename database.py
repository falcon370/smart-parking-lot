"""SQLite storage for vehicles, parking slots and payments."""

import os
import sqlite3
from contextlib import contextmanager

# Stored next to this file so the program finds its data from any folder.
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parking.db")


@contextmanager
def get_connection():
    """Open a connection, commit on success, roll back on error, always close."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


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
