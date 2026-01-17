import sqlite3

# Clean up corrupted history entries
conn = sqlite3.connect('memory.db')
cur = conn.cursor()

# Delete entries where query or search_query contains "object" or is too short
cur.execute("""
    DELETE FROM search_history 
    WHERE query LIKE '%object%' 
    OR search_query LIKE '%object%'
    OR LENGTH(search_query) < 3
""")

deleted = cur.rowcount
conn.commit()
conn.close()

print(f"✅ Deleted {deleted} corrupted history entries")
print("Your history is now clean!")
