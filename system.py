import sqlite3
import requests
import serpapi
import random
from datetime import datetime
conn = sqlite3.connect("data.db")
client = serpapi.Client(api_key="5386b5af7eda19abbe487a89b5e8dbb3a3504763f8691e718f505eed31640c03")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS flights (
    flight_ID TEXT,
    request_date TEXT,
    flight_date TEXT,
    flight_company TEXT,
    dep_air TEXT,
    arr_air TEXT,
    layover_air TEXT,
    priceEUR TEXT,
    primary_token TEXT PRIMARY KEY
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

def myTextFormat(text, length=20): # Kostya
    if len(text) > length:
        return text[:length-3] + "..."
    else:
        return text + " " * (length - len(text))

def cityToCode(city): # Kostya
    with open("airport-codes-new.txt", "r", encoding="utf-8") as f:
        airport_codes = f.readlines()
    for line in airport_codes:
        if line.split(",")[0] == city:
            return line.split(",")[2]
        if city in line:
            return line.split(",")[2]
    return None

def checkCity(city): # Kostya
    with open("airport-codes-new.txt", "r", encoding="utf-8") as f:
        airport_codes = f.readlines()
    for line in airport_codes:
        if line.split(',')[0] == city:
            return True
    return False

def searchInDBHotels(destination, check_in, check_out): # Kostya
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

def currentDate():
    today = datetime.today()
    formatedDate = today.strftime("%Y-%m-%d")
    return formatedDate

def checkSameDateForFlights():
    cursor.execute("SELECT request_date, flight_date, dep_air, arr_air FROM flights")
    exists_data = cursor.fetchall()
    conn.commit()
    return exists_data

def printAvalibleTickets():
    cursor.execute("SELECT flight_date, dep_air, arr_air, layover_air, priceEUR FROM flights")
    exists_data = cursor.fetchall()
    conn.commit()
    for i in exists_data:
        print(f"Date of departue: {i[0]}")
        print(f"Departue airport: {i[1]}")
        print(f"Arrival airport: {i[2]}")
        print(f"List of layover airports: {i[3]}")
        print(f"Price in EUR: {i[4]}")

def show_accommodation(destination, check_in, check_out): # Kostya
    cursor.execute('''SELECT * FROM hotelist
                    WHERE hotelDestination = ? AND hotelToken LIKE ? AND request_date = ?''', (destination, f"%{check_in}{check_out}%", datetime.today().strftime("%Y-%m-%d")))
    records = cursor.fetchall()
    print("________Name________ | Latitude | Longitude | Check-in | Check-out | Price for one night")
    for record in records:
        print(myTextFormat(record[3]), "|", myTextFormat(str(record[6]), 8), "|", myTextFormat(str(record[7]), 9), "|", myTextFormat(record[4], 8), "|", myTextFormat(record[5], 9), "|", myTextFormat(str(record[8]), 6))


# def requestAirports():
#     depAir = input("Enter departue airport(CODE): ")
#     arrAir = input("Enter arriving airport(CODE): ")
#     valid_date = False
#     while valid_date == False:
#         print("--------")
#         right_format = "%Y-%m-%d"
#         today = datetime.today()
#         formatedDate = today.strftime("%Y-%m-%d")
#         print(f"Current date: {formatedDate}")
#         dateOfDep = input("Enter date when you wish to fly(YYYY-MM-DD): ")
#         try:
#             if datetime.strptime(dateOfDep, right_format):
#                 valid_date = True
#                 print("The system is searching for ticket")
#                 break
#         except ValueError:
#             print("Wrong date. Try again")
#     list_of_data = {"depAir": depAir, "arrAir": arrAir, "dateOfDep": dateOfDep}
#     return list_of_data

def genInput(tr_type = "ret"):
    depAir = input("Enter departure city: ")
    while checkCity(depAir) == False:
        print("City not found. Please try again.")
        depAir = input("Enter departure city: ")
    arrAir = input("Enter arrival city: ")
    while checkCity(arrAir) == False:
        print("City not found. Please try again.")
        arrAir = input("Enter arrival city: ")
    valid_date = False
    while valid_date == False:
        print("--------")
        right_format = "%Y-%m-%d"
        today = datetime.today()
        print("Today's date is:", today.strftime(right_format))    
        dateOfDep = input("Enter date of departure (YYYY-MM-DD): ")
        try:
            dep_date = datetime.strptime(dateOfDep, right_format)
            if dep_date < today:
                print("Date cannot be in the past. Please try again.")
            else:
                valid_date = True
        except ValueError:
            print("Invalid date format. Please try again.")
    valid_date = False
    while valid_date == False:
        print("--------")
        right_format = "%Y-%m-%d"
        today = datetime.today()
        print("Today's date is:", today.strftime(right_format))    
        dateOfReturn = input("Enter date of return (YYYY-MM-DD): ")
        try:
            ret_date = datetime.strptime(dateOfReturn, right_format)
            if ret_date < today:
                print("Date cannot be in the past. Please try again.")
            else:
                valid_date = True
        except ValueError:
            print("Invalid date format. Please try again.")
    return {"depAir": depAir, "arrAir": arrAir, "dateOfDep": dateOfDep, "dateOfReturn": dateOfReturn}

def loadDataToBase(flights_list):
    for j in range(len(flights_list)):
        try:
            flight = flights_list[j]["flights"][0]
            listoftick = (
                flight["flight_number"],
                currentDate(),
                flight["departure_airport"]["time"][:10],
                flight["airline"],
                flight["departure_airport"]["id"],
                flights_list[j]["flights"][-1]["arrival_airport"]["id"],
                ",".join([i["id"] for i in flights_list[j]["layovers"]]),
                int(flights_list[j]["price"]),
                str(random.random()),
            )
        except KeyError:
            flight = flights_list[j]["flights"][0]
            listoftick = (
                flight["flight_number"],
                currentDate(),
                flight["departure_airport"]["time"][:10],
                flight["airline"],
                flight["departure_airport"]["id"],
                flights_list[j]["flights"][-1]["arrival_airport"]["id"],
                "0",
                int(flights_list[j]["price"]),
                str(random.random()),
            )
        cursor.execute("INSERT INTO flights (flight_ID, request_date, flight_date, flight_company, dep_air, arr_air, layover_air, priceEUR, primary_token) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", listoftick)
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

def findOneWayFlights(data):
    exists_data = checkSameDateForFlights()
    if exists_data != []:
        for i in exists_data:
            if not (i[0] == currentDate() and i[1] == data["dateOfDep"] and i[2] == data["depAir"] and i[3] == data["arrAir"]):
                tickets = requestAirAPI(cityToCode(data["depAir"]), cityToCode(data["arrAir"]), data["dateOfDep"])
                loadDataToBase(tickets)
                printAvalibleTickets()
            else:
                print("AMOGUS")
    else:
        tickets = requestAirAPI(cityToCode(data["depAir"]), cityToCode(data["arrAir"]), data["dateOfDep"])
        loadDataToBase(tickets)
        printAvalibleTickets()

def find_accommodation(destination, check_in, check_out): # Kostya
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

def menu():
    while True:
        print("1. Search for a one-way flight")
        print("2. Search for hotels")
        print("3. Search for a round-trip flight and a hotel")
        print("4. Exit")
        choice = input("Please enter your choice (1-4): ")
        if choice>="1" and choice<"4":
            tr_dat = genInput("ret" if choice == "3" else "hotel_only" if choice == "2" else "one way")
        match choice:
            case "1":
                findOneWayFlights(tr_dat)
            case "2":
                destination = tr_dat["arrAir"] 
                check_in = tr_dat["dateOfDep"]
                check_out = tr_dat["dateOfReturn"]
                if searchInDBHotels(destination, check_in, check_out) == []:
                    find_accommodation(destination, check_in, check_out)
                    print("DEV: Hotel data has been saved to the database.")
                else:
                    print("DEV: Hotel data already exists in the database.")
                show_accommodation(destination, check_in, check_out)
            case "3":
                destination = tr_dat["arrAir"] 
                check_in = tr_dat["dateOfDep"]
                check_out = tr_dat["dateOfReturn"] 
                findOneWayFlights(tr_dat)
                findOneWayFlights({"depAir": tr_dat["arrAir"], "arrAir" : tr_dat["depAir"], "dateOfDep":tr_dat["dateOfReturn"]})
                if searchInDBHotels(destination, check_in, check_out) == []: # still not sure how to pass data from the flight fun to the hotels one
                    find_accommodation(destination, check_in, check_out)
                    print("DEV: Hotel data has been saved to the database.")
                else:
                    print("DEV: Hotel data already exists in the database.")
                show_accommodation(destination, check_in, check_out)
            case "4":
                break
            case _:
                print("Invalid choice. Please try again.")
    conn.close()

menu()