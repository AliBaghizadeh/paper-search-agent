import sqlite3
import json

def check_db():
    try:
        conn = sqlite3.connect('memory.db')
        cur = conn.cursor()
        cur.execute("SELECT id, query, search_query FROM search_history ORDER BY id DESC LIMIT 10")
        rows = cur.fetchall()
        print("Last 10 search history entries:")
        for r in rows:
            print(f"ID: {r[0]} | Query: {r[1]} | Keywords: {r[2]}")
        conn.close()
    except Exception as e:
        print(f"Error checking DB: {e}")

if __name__ == "__main__":
    check_db()
