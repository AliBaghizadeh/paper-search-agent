from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional, Any
from pathlib import Path
import sqlite3
import json
from datetime import datetime

DB_PATH = Path(__file__).parent / "memory.db"

app = FastAPI(title="Search Memory API", description="Backend for storing search history and paper results.")

class SearchLog(BaseModel):
    query: Any
    search_query: Any
    top_results: List[Any] = []

def get_conn():
    return sqlite3.connect(DB_PATH, timeout=20.0, check_same_thread=False)

@app.post("/log_search")
def log_search(payload: SearchLog):
    """Log a search query and its top results to the SQLite database."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO search_history (query, search_query, top_results, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                str(payload.query),
                str(payload.search_query),
                json.dumps(payload.top_results, ensure_ascii=False),
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()
        last_id = cur.lastrowid
        conn.close()
        print(f"Logged search ID: {last_id}")
        return {"status": "ok", "id": last_id}
    except Exception as e:
        print(f"Database error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/history")
def history(limit: int = 10):
    """Retrieve the recent search history."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, query, search_query, top_results, created_at
            FROM search_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
        conn.close()

        result = []
        for r in rows:
            result.append(
                {
                    "id": r[0],
                    "query": r[1],
                    "search_query": r[2],
                    "top_results": json.loads(r[3]) if r[3] else [],
                    "created_at": r[4],
                }
            )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}