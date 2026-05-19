import sqlite3
import requests
import serpapi
from datetime import datetime
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS flights (
    flight_date INTEGER PRIMARY KEY AUTOINCREMENT,
    dep_air TEXT,
    arr_air TEXT,
    flight_id TEXT
    
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS trains (
    train_number INTEGER PRIMARY KEY AUTOINCREMENT,
    train_station TEXT,
    train_date TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS buses (
    bus_number INTEGER PRIMARY KEY AUTOINCREMENT,
    bus_station TEXT,
    bus_date TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS hotelist (
    hotelNumber INTEGER PRIMARY KEY AUTOINCREMENT,
    hotelName TEXT,
    hotelAdress TEXT,
    Price for one night INTEGER
    )
''')

conn.commit()

flightBase = ""
transferBase = ""
hotelBase = ""

def get_json(url, params=None, headers=None):
    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=30 # fail fast if API is unresponsive
    )
    response.raise_for_status() 
    return response.json()

def getJopa(base):
    url = f"{base}.json"
    data = get_json(url, params={"limit": 100})
    finaldata = data
    return finaldata

def requestAirports():
    depAir = input("Enter departue airport(CODE): ")
    arrAir = input("Enter arriving airport(CODE): ")
    valid_date = False
    while valid_date == False:
        print("--------")
        right_format = "%d-%m-%Y"
        today = datetime.today()
        formatedDate = today.strftime("%d-%m-%Y")
        print(f"Current date: {formatedDate}")
        dateOfDep = input("Enter date when you wish to fly(DD-MM-YYYY): ")
        try:
            if datetime.strptime(dateOfDep, right_format):
                valid_date = True
                print("The system is searching for ticket")
                break
        except ValueError:
            print("Wrong date. Try again")
    list_of_data = [depAir, arrAir, dateOfDep]
    return list_of_data


print("Welcome to JOPA")
data = requestAirports()
depAir = data[0]
arrAir = data[1]
date_of_dep = data[3]
