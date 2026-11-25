import os
import re
import sqlite3
import pathlib
from typing import Dict, Any, List, Optional

DB_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / "data" / "kacang_dwh.db"

# Optional psycopg2 import
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


class PostgresCursorWrapper:
    """Wrapper around psycopg2 cursor to make it act like SQLite cursor with '?' placeholder, dict/tuple row access."""
    def __init__(self, raw_cursor):
        self._cur = raw_cursor

    def _convert_sql(self, sql: str) -> str:
        # 1. Convert ? placeholder to %s
        s = sql.replace("?", "%s")
        # 2. Convert SQLite DDL to PostgreSQL compatible syntax
        s = re.sub(r'INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT', 'SERIAL PRIMARY KEY', s, flags=re.IGNORECASE)
        s = re.sub(r'\bAUTOINCREMENT\b', '', s, flags=re.IGNORECASE)
        # 3. Handle datetime('now') to NOW()
        s = re.sub(r"datetime\('now'\)", 'NOW()', s, flags=re.IGNORECASE)
        return s

    def execute(self, sql: str, params: Optional[Any] = None):
        converted_sql = self._convert_sql(sql)
        if params is not None:
            if isinstance(params, list):
                params = tuple(params)
            return self._cur.execute(converted_sql, params)
        return self._cur.execute(converted_sql)

    def executemany(self, sql: str, seq_of_parameters: Any):
        converted_sql = self._convert_sql(sql)
        return self._cur.executemany(converted_sql, seq_of_parameters)

    def fetchone(self):
        row = self._cur.fetchone()
        if row is None:
            return None
        return RowWrapper(dict(row))

    def fetchall(self):
        rows = self._cur.fetchall()
        return [RowWrapper(dict(r)) for r in rows]

    @property
    def rowcount(self):
        return self._cur.rowcount

    @property
    def description(self):
        return self._cur.description


class RowWrapper(dict):
    """Allows dict access by key as well as numeric index (like sqlite3.Row)."""
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


class PostgresConnectionWrapper:
    """Wrapper around psycopg2 connection."""
    def __init__(self, raw_conn):
        self._conn = raw_conn

    def cursor(self):
        return PostgresCursorWrapper(self._conn.cursor(cursor_factory=RealDictCursor))

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()


def get_db():
    """
    Connect to PostgreSQL if configured (or DATABASE_URL / POSTGRES_HOST present),
    otherwise gracefully fall back to local SQLite database.
    """
    db_type = os.getenv("DB_TYPE", "").lower()
    db_url = os.getenv("DATABASE_URL")
    pg_host = os.getenv("POSTGRES_HOST")

    if PSYCOPG2_AVAILABLE and (db_type == "postgresql" or db_url or pg_host):
        try:
            if db_url:
                conn = psycopg2.connect(db_url)
            else:
                conn = psycopg2.connect(
                    host=pg_host or "localhost",
                    port=int(os.getenv("POSTGRES_PORT", "5432")),
                    dbname=os.getenv("POSTGRES_DB", "duakelinci_dwh"),
                    user=os.getenv("POSTGRES_USER", "duakelinci_user"),
                    password=os.getenv("POSTGRES_PASSWORD", "***REMOVED***")
                )
            return PostgresConnectionWrapper(conn)
        except Exception as e:
            # Fall back to SQLite if PostgreSQL connection fails
            print(f"[WARN] PostgreSQL connection failed ({e}), falling back to SQLite: {DB_PATH}")

    # Fallback to SQLite
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn
