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


cursor.execute('''
    CREATE TABLE IF NOT EXISTS hotels (
    token TEXT PRIMARY KEY, 
    name TEXT, 
    latitude REAL,
    longitude REAL,
    check_in_time TEXT,
    check_out_time TEXT,
    rent_per_night REAL
    )
    ''')
conn.commit()
conn.close()

def find_accommodation(destination, check_in, check_out):
    hotel_search_results = client.search({
      "engine": "google_hotels",
      "q": destination,
      "check_in_date": check_in,
      "check_out_date": check_out,
    })
    properties = hotel_search_results["properties"]
    for i in properties:
        cursor.execute('''
        INSERT INTO hotels (token, name, latitude, longitude, check_in, check_out, per_night)
        VALUES(?, ?, ?, ?, ?, ?, ?)'''), i["property_token"], i["name"], i["gps_coordinates"]["latitude"], i["gps_coordinates"]["longitude"], i["check_in_time"], i["check_out_time"], i["rent_per_night"]["extracted_lowest"]
        cursor.commit()
        cursor.close()

def show_accommodation(destination, check_in, check_out):
    cursor.executemany('''
        SELECT * FROM hotels
                    ''')
    records = cursor.fetchall()
    cursor.close()
    print("Name | smth")
    for record in records:
        print(record)
