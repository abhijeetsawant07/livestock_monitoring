import time
import random
import requests
import threading
import os
from flask import Flask

app = Flask(__name__)

URL = "https://livestock-monitoring.onrender.com/sensor-data"
#URL = "http://localhost:5001/sensor-data"
GOATS = ["goat_1", "goat_2", "goat_3"]
print("...Simulator started...")

def run_simulator():
    print("Simulator started...")

    while True:
        for goat in GOATS:
            try:
                if goat == "goat_1":
                    temp = round(random.uniform(38, 39), 2)
                    movement = random.randint(10, 20)
                    feed = random.randint(300, 500)

                elif goat == "goat_2":
                    temp = round(random.uniform(39, 41), 2)
                    movement = random.randint(0, 5)
                    feed = random.randint(100, 200)

                else:
                    temp = round(random.uniform(38, 40), 2)
                    movement = random.randint(5, 15)
                    feed = random.randint(150, 350)

                data = {
                    "goat_id": goat,
                    "temperature": temp,
                    #"movement": movement,
                    "movement": 0,
                    "feed": feed
                }

                res = requests.post(URL, json=data, timeout=5)
                print("Data Sent:", data)

            except Exception as e:
                print("Error:", e)

        time.sleep(5)

@app.route("/")
def home():
    return "MyFirstData.db"

if __name__ == "__main__":
    # Start simulator thread
    thread = threading.Thread(target=run_simulator)
    thread.daemon = True
    thread.start()

    # Start Flask server (THIS is what Render needs)
    port = int(os.environ.get("PORT", 10000))
    print(f"Server starting on port {port}")

    app.run(host="0.0.0.0", port=port)
