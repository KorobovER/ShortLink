"""Database module for SQLite operations."""

import sqlite3
from pathlib import Path
from typing import Optional


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
        self._connection: Optional[sqlite3.Connection] = None
    
    def connect(self) -> sqlite3.Connection:
        """Connect to database and create connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def initialize(self) -> None:
        """Initialize database tables."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT UNIQUE NOT NULL,
                original_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                clicks INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute SQL query."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor
    
    def fetchone(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Execute query and fetch one row."""
        cursor = self.execute(query, params)
        return cursor.fetchone()
    
    def fetchall(self, query: str, params: tuple = ()) -> list[sqlite3.Row]:
        """Execute query and fetch all rows."""
        cursor = self.execute(query, params)
        return cursor.fetchall()
    
    def commit(self) -> None:
        """Commit transaction."""
        conn = self.connect()
        conn.commit()
    
    def __enter__(self) -> "Database":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        """Context manager exit."""
        self.disconnect()


# Global database instance
db = Database()
