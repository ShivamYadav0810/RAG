import sqlite3
from contextlib import contextmanager
from typing import Any, Generator
import logging
from fastapi import HTTPException
from config import settings

conn = sqlite3.connect(settings.DATABASE_URL, check_same_thread=False)

@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager to handle database connections.
    """
    try:
        yield conn
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    finally:
        conn.commit()