"""SQLite storage for vehicles, parking slots and payments.

Tables:
    vehicles       one row per plate number ever seen
    parking_slots  one row per slot, with its occupied flag
    payments       one row per parking session; exit_time and amount stay
                   NULL while the vehicle is still parked
"""

import os
import sqlite3
from contextlib import contextmanager

# Database file kept next to this source file, so the program finds the same
# data whichever folder it is started from. Tests replace this with a temp file.
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parking.db")


@contextmanager
def get_connection():
    """Open a database connection for use in a ``with`` block.

    Changes are committed when the block ends normally, rolled back if an
    exception is raised inside it, and the connection is always closed.
    Rows can be read by column name (``row["plate_number"]``).

    Example:
        with get_connection() as conn:
            conn.execute("UPDATE parking_slots SET is_occupied = 1 WHERE slot_id = 1")
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # enforce REFERENCES constraints
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create the three tables if they do not exist yet. Safe to call every run."""
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
