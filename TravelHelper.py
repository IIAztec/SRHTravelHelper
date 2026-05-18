import sqlite3
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS flights (
    flight_number INTEGER PRIMARY KEY AUTOINCREMENT,
    dep_air TEXT,
    arr_air TEXT,
    flight_date TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS trains (
    train_number INTEGER PRIMARY KEY AUTOINCREMENT,
    train_station TEXT,
    train_date TEXT
    )
''')
conn.commit()
conn.close()
