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
    request_date TEXT,
    flight_date TEXT,
    flight_company TEXT,
    dep_air TEXT,
    arr_air TEXT,
    layover_air TEXT,
    priceEUR TEXT,
    booking_token TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS hotelist (
    hotelToken TEXT PRIMARY KEY,
    hotelDestination TEXT,
    request_date TEXT,
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

def currentDate():
    today = datetime.today()
    formatedDate = today.strftime("%Y-%m-%d")
    return formatedDate

def checkSameDateForFlights():
    cursor.execute("SELECT request_date, dep_air, arr_air FROM flights")
    exists_data = cursor.fetchall()
    print(exists_data)
    conn.commit()


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
        currentDate(),
        flight["departure_airport"]["time"][:10],
        flight["airline"],
        flight["departure_airport"]["id"],
        flight["arrival_airport"]["id"],
        int(flights_list[0]["price"]),
    )
    cursor.execute("INSERT INTO flights (flight_ID, request_date, flight_date, flight_company, dep_air, arr_air, priceEUR) VALUES (?, ?, ?, ?, ?, ?, ?)", listoftick)
    conn.commit()

# def loadPriceToData(flight_list):
#     price = flight_list[0]
#     pricelist = (
#         int(price["price"]),
#     )
#     cursor.execute("INSERT INTO flights (priceEUR) VALUES (?)", pricelist)
#     conn.commit()

def loadLayOverAir(fligt_list):
    air = fligt_list[0]["flights"]["layovers"][0]


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
# loadPriceToData(tickets)
checkSameDateForFlights()
