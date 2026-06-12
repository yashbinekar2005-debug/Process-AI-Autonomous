import sqlite3
import os

DB_FILE = "enterprise_local.db"

def init_db():
    """
    Initializes a local database for demonstrating actions, competitor intelligence, and tickets.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'OPEN',
            assigned_agent TEXT,
            priority TEXT DEFAULT 'MEDIUM',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS competitor_intel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            key_finding TEXT,
            source_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def execute_query(query: str, params: tuple = ()) -> str:
    """
    Executes a SQL query and returns results.
    
    Args:
        query (str): SQL query to execute.
        params (tuple): Parameters for safe parameter substitution.
        
    Returns:
        str: String representation of query results or status.
    """
    init_db()
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Guard rails
        if not query.strip().upper().startswith(("SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "PRAGMA")):
            conn.close()
            return "Query Rejected: Unauthorized SQL command prefix."
            
        cursor.execute(query, params)
        
        if query.strip().upper().startswith(("SELECT", "PRAGMA")):
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            conn.close()
            return str(results)
        else:
            conn.commit()
            changes = conn.total_changes
            conn.close()
            return f"Query executed successfully. Rows changed: {changes}"
    except Exception as e:
        return f"Database Error: {str(e)}"
