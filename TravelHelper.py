import sqlite3
import requests
import serpapi
from datetime import datetime
conn = sqlite3.connect("data.db")
client = serpapi.Client(api_key="5386b5af7eda19abbe487a89b5e8dbb3a3504763f8691e718f505eed31640c03")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS flights (
    flight_ID TEXT PRIMARY KEY,
    flight_date TEXT,
    flight_company TEXT,
    dep_air TEXT,
    arr_air TEXT,
    booking_token
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
    hotelToken TEXT PRIMARY KEY,
    hotelName TEXT,
    timeOfCheckIn TEXT,
    timeOfCheckOut TEXT,
    hotelLongitude REAL,
    hotelLaditude REAL,
    PriceForOneNight REAL,
    BookingURL TEXT
    )
''')

conn.commit()

def searchInDBHotels(destination, check_in, check_out):
    cursor.execute('''
        SELECT hotelToken FROM hotelist WHERE hotelDestination = ? AND request_date = ?
                    ''', (destination, datetime.today().strftime("%Y-%m-%d")))
    hotelTokens = cursor.fetchall()
    index = 0
    while index < len(hotelTokens):
        if hotelTokens[index][0].find(check_in) == -1 or hotelTokens[index][0].find(check_out) == -1:
            hotelTokens.remove(hotelTokens[index])
        else:
            index += 1
    return hotelTokens

def find_accommodation(destination, check_in, check_out):
    hotel_search_results = client.search({
        "engine": "google_hotels",
        "q": destination,
        "check_in_date": check_in,
        "check_out_date": check_out,
    })
    properties = hotel_search_results["properties"]
    for i in properties:
        try:
            hotel_data = (i["property_token"]+check_in+check_out, destination, datetime.today().strftime("%Y-%m-%d"), i["name"], i["gps_coordinates"]["latitude"], i["gps_coordinates"]["longitude"], i["check_in_time"], i["check_out_time"], i["rate_per_night"]["lowest"],)
            cursor.execute('''
            INSERT INTO hotelist (hotelToken, hotelDestination, request_date, hotelName, hotelLaditude, hotelLongitude, timeOfCheckIn, timeOfCheckOut, PriceForOneNight)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)''', hotel_data)
            conn.commit()
        except KeyError:
            continue



def show_accommodation(destination, check_in, check_out):
    cursor.execute('''SELECT * FROM hotelist
                    WHERE hotelDestination = ? AND hotelToken LIKE ? AND request_date = ?''', (destination, f"%{check_in}{check_out}%", datetime.today().strftime("%Y-%m-%d")))
    records = cursor.fetchall()
    print("Name | Check-in | Check-out | Latitude | Longitude | Price for one night")
    for record in records:
        print(record[3], "|", record[6], "|", record[7], "|", record[4], "|", record[5], "|", record[8])

def requestAirports():
    depAir = input("Enter departue airport(CODE): ")
    arrAir = input("Enter arriving airport(CODE): ")
    valid_date = False
    while valid_date == False:
        print("--------")
        right_format = "%Y-%m-%d"
        today = datetime.today()
        formatedDate = today.strftime("%Y-%m-%d")
        print(f"Current date: {formatedDate}")
        dateOfDep = input("Enter date when you wish to fly(YYYY-MM-DD): ")
        try:
            if datetime.strptime(dateOfDep, right_format):
                valid_date = True
                print("The system is searching for ticket")
                break
        except ValueError:
            print("Wrong date. Try again")
    list_of_data = {"depair": depAir, "arrAir": arrAir, "dateOfDep": dateOfDep}
    return list_of_data

def loadDataToBase(flights_list):
    flight = flights_list[0]["flights"][0]
    listoftick = (
        flight["flight_number"],
        flight["departure_airport"]["time"][:10],
        flight["airline"],
        flight["departure_airport"]["id"],
        flight["arrival_airport"]["id"],
    )
    cursor.execute("INSERT INTO flights (flight_ID, flight_date, flight_company, dep_air, arr_air) VALUES (?, ?, ?, ?, ?)", listoftick)
    conn.commit()

def requestAirAPI(dep, arr, date):
    results = client.search({
    "engine": "google_flights",
    "departure_id": dep,
    "arrival_id": arr,
    "currency": "EUR",
    "type": "2",
    "outbound_date": date
    })
    best_flights = results["best_flights"]
    return best_flights

def menu():
    print("Welcome to TravelHelper!")
    print("1. Search for flights")
    print("2. Search for hotels")
    print("3. Exit")
    while True:
        choice = input("Please enter your choice (1-3): ")
        match choice:
            case "1":
                flight_data = requestAirports()
                best_flights = requestAirAPI(flight_data["depair"], flight_data["arrAir"], flight_data["dateOfDep"])
                loadDataToBase(best_flights)
                print("DEV:Flight data has been saved to the database.")
            case "2":
                destination = input("Enter your destination: ")
                check_in = input("Enter check-in date (YYYY-MM-DD): ")
                check_out = input("Enter check-out date (YYYY-MM-DD): ")
                if searchInDBHotels(destination, check_in, check_out) == []:
                    find_accommodation(destination, check_in, check_out)
                    print("DEV: Hotel data has been saved to the database.")
                else:
                    print("DEV: Hotel data already exists in the database.")
                show_accommodation(destination, check_in, check_out)
            case "3":
                break
            case _:
                print("Invalid choice. Please try again.")
    conn.close()

menu()
