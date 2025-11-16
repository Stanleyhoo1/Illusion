import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "cache.db"


def init_db():
    """Initialize the SQLite database with schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Companies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            resolved_domain TEXT,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Sources table (from search_result)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            policy_type TEXT,
            title TEXT,
            summary TEXT,
            relevance REAL,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)

    # Extracted points table (from extraction_result)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extracted_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            source_url TEXT,
            content_summary TEXT,
            point_text TEXT,
            relevance REAL,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)

    # Cache metadata (for TTL and full response)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL UNIQUE,
            full_response TEXT NOT NULL,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)

    conn.commit()
    conn.close()


def get_cached_response(company_name: str, ttl_days: int = 7) -> dict | None:
    """
    Retrieve cached response for a company if it exists and is fresh.

    Args:
        company_name: The company to look up
        ttl_days: Cache TTL in days (default 7)

    Returns:
        Cached response dict or None if not found/expired
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT cm.full_response, cm.cached_at 
            FROM cache_metadata cm
            JOIN companies c ON cm.company_id = c.id
            WHERE c.name = ? AND 
                  datetime(cm.cached_at, '+' || ? || ' days') > datetime('now')
        """,
            (company_name, ttl_days),
        )

        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None
    finally:
        conn.close()


def cache_response(company_name: str, resolved_domain: str, response_data: dict):
    """
    Cache the API response in the database.

    Args:
        company_name: Company name
        resolved_domain: Resolved domain from search_result
        response_data: Full API response dict
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Insert or get company
        cursor.execute(
            "INSERT OR IGNORE INTO companies (name, resolved_domain) VALUES (?, ?)",
            (company_name, resolved_domain),
        )
        cursor.execute("SELECT id FROM companies WHERE name = ?", (company_name,))
        company_id = cursor.fetchone()[0]

        # Clear old data for this company
        cursor.execute("DELETE FROM sources WHERE company_id = ?", (company_id,))
        cursor.execute(
            "DELETE FROM extracted_points WHERE company_id = ?", (company_id,)
        )
        cursor.execute("DELETE FROM cache_metadata WHERE company_id = ?", (company_id,))

        # Cache sources from search_result
        if response_data.get("search_result", {}).get("sources"):
            for source in response_data["search_result"]["sources"]:
                cursor.execute(
                    """
                    INSERT INTO sources (company_id, url, policy_type, title, summary, relevance)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        company_id,
                        source.get("url"),
                        source.get("policy_type"),
                        source.get("title"),
                        source.get("summary"),
                        source.get("relevance"),
                    ),
                )

        # Cache extracted points from extraction_result
        if response_data.get("extraction_result", {}).get("results"):
            for result in response_data["extraction_result"]["results"]:
                for point in result.get("extracted_points", []):
                    cursor.execute(
                        """
                        INSERT INTO extracted_points (company_id, source_url, content_summary, point_text, relevance)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            company_id,
                            result.get("url"),
                            result.get("content_summary"),
                            point,
                            result.get("relevance"),
                        ),
                    )

        # Cache full response
        cursor.execute(
            "INSERT INTO cache_metadata (company_id, full_response) VALUES (?, ?)",
            (company_id, json.dumps(response_data)),
        )

        conn.commit()
    finally:
        conn.close()


def clear_expired_cache(ttl_days: int = 7):
    """Remove cache entries older than TTL."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM cache_metadata 
            WHERE datetime(cached_at, '+' || ? || ' days') <= datetime('now')
        """,
            (ttl_days,),
        )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
