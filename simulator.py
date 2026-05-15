import requests
import random
import time
from flask import Flask

URL = "https://livestock-monitoring.onrender.com/sensor-data"
#URL = "http://localhost:5001/sensor-data"
GOATS = ["goat_1", "goat_2", "goat_3"]
print("...Simulator started...")

while True:
    for goat in GOATS:
        # Simulate different behavior per goat
        try:
            # --- Simulate behavior ---
            if goat == "goat_1":
                temp = round(random.uniform(38, 39), 2)
                movement = random.randint(10, 20)
                feed = random.randint(300, 500)

            elif goat == "goat_2":
                temp = round(random.uniform(39, 41), 2)
                movement = random.randint(0, 5)
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

            response = requests.post(URL, json=data, timeout=5)

            if response.status_code == 200:
                print("Data Sent:", data)
            else:
                print("Failed:", response.text)

        except Exception as e:
            print("Error sending data:", str(e))

    time.sleep(5)

# flask server starting
if __name__ == "__main__":
    import threading
    import os

    # Start simulator in background
    thread = threading.Thread(target=run_simulator)
    thread.daemon = True
    thread.start()

    # Start Flask server (THIS is critical)
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Starting server on port {port}...")

    app.run(host="0.0.0.0", port=port)
