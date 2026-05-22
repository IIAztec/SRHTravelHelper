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

def loadDataToBase(json):
    listoftick = [
        json[0]["flights"][0]["flight_number"], 
        json[0]["flights"][0]["departure_airport"]["time"][:10],
        json[0]["flights"][0]["airline"], 
        json[0]["flights"][0]["departure_airport"]["id"], 
        json[0]["flights"][0]["arrival_airport"]["id"], 
        # json["booking_token"]
    ]
    cursor.execute("INSERT INTO flights (flight_ID, flight_date, flight_company, dep_air, arr_air, booking_token) VALUES (?, ?, ?, ?, ?, ?, ?) ", listoftick)
    conn.commit()
    conn.close()

def requestAirAPI(dep, arr, date):
    results = client.search({
    "engine": "google_flights",
    "departure_id": dep,
    "arrival_id": arr,
    "currency": "EUR",
    "type": "2",
    "outbound_date": date
    })
    best_flights= results["best_flights"]


# def printAvailibleflights(json):
    


print("Welcome to JOPA")
data = requestAirports()
tickets = requestAirAPI(data["depair"], data["arrAir"], data["dateOfDep"])
# loadDataToBase(tickets)
print(tickets)