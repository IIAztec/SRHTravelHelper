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

def getAPIData(base):
    url = f"{base}.json"
    data = get_json(url, params={"limit": 100})
    finaldata = data
    return finaldata

def myTextFormat(text, length=20):
    if len(text) > length:
        return text[:length-3] + "..."
    else:
        return text + " " * (length - len(text))

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
    print("________Name________ | Latitude | Longitude | Check-in | Check-out | Price for one night")
    for record in records:
        print(myTextFormat(record[3]), "|", myTextFormat(str(record[6]), 8), "|", myTextFormat(str(record[7]), 9), "|", myTextFormat(record[4], 8), "|", myTextFormat(record[5], 9), "|", myTextFormat(str(record[8]), 6))

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


# def printAvailibleflights(json):
    


print("Welcome to JOPA")
data = requestAirports()
tickets = requestAirAPI(data["depair"], data["arrAir"], data["dateOfDep"])
loadDataToBase(tickets)
print(tickets)
