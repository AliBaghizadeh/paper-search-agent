import sqlite3
import time
import os
from datetime import datetime

DB_PATH = "memory.db"

def watch_db():
    last_id = -1
    print(f"🔬 SURGERY KIT: Watching {DB_PATH} for new rows...")
    print("Press CTRL+C to stop.")
    
    while True:
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT id, query, created_at FROM search_history ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
            conn.close()
            
            if row:
                current_id = row[0]
                if current_id != last_id:
                    print(f"\n✨ NEW ROW DETECTED at {datetime.now().strftime('%H:%M:%S')}")
                    print(f"   ID: {current_id}")
                    print(f"   Query: {row[1]}")
                    print(f"   Timestamp: {row[2]}")
                    last_id = current_id
            
        except sqlite3.OperationalError as e:
            # Handle potential locks silently
            pass
        except Exception as e:
            print(f"Error: {e}")
            
        time.sleep(1)

if __name__ == "__main__":
    watch_db()
