import requests
import random
import time

URL = "https://livestock-monitoring.onrender.com/sensor-data"
#URL = "http://localhost:5001/sensor-data"
GOATS = ["goat_1", "goat_2", "goat_3"]

while True:
    for goat in GOATS:
        # Simulate different behavior per goat
        if goat == "goat_1":
            temp = round(random.uniform(38, 39), 2)
            movement = random.randint(10, 20)
            feed = random.randint(300, 500)

        elif goat == "goat_2":
            temp = round(random.uniform(39, 41), 2)  # slightly high
            movement = random.randint(0, 5)           # low movement
            feed = random.randint(100, 200)

        else:  # goat_3
            temp = round(random.uniform(38, 40), 2)
            movement = random.randint(5, 15)
            feed = random.randint(150, 350)

        data = {
            "goat_id": goat,
            "temperature": temp,
            "movement": movement,
            "feed": feed
        }

        requests.post(URL, json=data)
        print("Sent:", data)

    time.sleep(5)
