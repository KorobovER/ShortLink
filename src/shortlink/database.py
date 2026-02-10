"""Database module for SQLite operations."""

import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager


class Database:
    """SQLite database manager."""
    
    def __init__(self, db_path: Optional[str] = None) -> None:
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file. If None, uses 'shortlink.db'.
        """
        if db_path is None:
            db_path = "shortlink.db"
        
        self.db_path = Path(db_path)
    
    @contextmanager
    def get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def initialize(self) -> None:
        """Initialize database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_code TEXT UNIQUE NOT NULL,
                    original_url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute SQL query."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor
    
    def fetchone(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Execute query and fetch one row."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def fetchall(self, query: str, params: tuple = ()) -> list[sqlite3.Row]:
        """Execute query and fetch all rows."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def add_link(self, short_code: str, original_url: str) -> None:
        """Add new link to database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO links (short_code, original_url) VALUES (?, ?)",
                (short_code, original_url)
            )
            conn.commit()
    
    def get_link_by_short_code(self, short_code: str) -> Optional[sqlite3.Row]:
        """Get link by short code."""
        return self.fetchone(
            "SELECT * FROM links WHERE short_code = ?",
            (short_code,)
        )
    
    def get_link_by_original_url(self, original_url: str) -> Optional[sqlite3.Row]:
        """Get link by original URL."""
        return self.fetchone(
            "SELECT * FROM links WHERE original_url = ?",
            (original_url,)
        )


# Global database instance
db = Database()
