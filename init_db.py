import sqlite3
from pathlib import Path

db_path = Path("memory.db")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.executescript("""
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    search_query TEXT NOT NULL,
    top_results TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT,
    title TEXT NOT NULL,
    authors_venue_year TEXT,
    year TEXT,
    source TEXT,
    link TEXT,
    snippet TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()
conn.close()

print("Initialized memory.db with search_history and favorites tables.")