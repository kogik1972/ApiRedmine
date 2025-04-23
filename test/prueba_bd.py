import sqlite3
try:
    conn = sqlite3.connect("instance/firma.db")
    print("¡Se abrió correctamente!")
    conn.close()
except Exception as e:
    print("Error:", e)
