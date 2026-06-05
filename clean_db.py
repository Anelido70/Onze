import sqlite3
conn = sqlite3.connect("football_manager.db")
conn.execute("DELETE FROM suspensions")
conn.execute("DELETE FROM match_events")
conn.execute("DELETE FROM matches")
conn.commit()
conn.close()
print("✅ Base de datos limpia. Simula partidos nuevos.")