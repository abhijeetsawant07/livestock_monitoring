import time
import requests
from collections import defaultdict, deque
from db import get_conn


class GoatHealthMonitor:
    def __init__(self, token, chat_id):
        self.TOKEN = token
        self.CHAT_ID = chat_id

        self.history = defaultdict(lambda: deque(maxlen=60))
        self.baseline = {}
        self.goat_status = {}
        self.last_alert_time = {}

        # NEW: sustained movement tracking
        self.low_movement_counter = defaultdict(int)

        self.COOLDOWN = 300
        self.BASELINE_SIZE = 30

    # ----------------------------
    def should_send(self, goat_id, condition):
        key = (goat_id, condition)
        now = time.time()

        if key in self.last_alert_time and (now - self.last_alert_time[key] < self.COOLDOWN):
            return False

        self.last_alert_time[key] = now
        return True

    # ----------------------------
    def save_alert(self, goat_id, alerts):
        conn = get_conn()
        cur = conn.cursor()

        for alert in alerts:
            cur.execute("""
            INSERT INTO alerts (goat_id, alert, timestamp)
            VALUES (?, ?, ?)
            """, (
                goat_id,
                alert,
                time.strftime("%Y-%m-%d %H:%M:%S")
            ))

        conn.commit()
        conn.close()

    # ----------------------------
    def send_alert(self, alerts, data):
        message = f"ALERT for {data['goat_id']}\n"

        for alert in alerts:
            message += f"- {alert}\n"

        message += (
            f"\nTemp: {data['temperature']}, "
            f"Movement: {data['movement']}, "
            f"Feed: {data['feed']}"
        )

        print(message)

        url = f"https://api.telegram.org/bot{self.TOKEN}/sendMessage"

        try:
            response = requests.post(url, json={
                "chat_id": self.CHAT_ID,
                "text": message
            })

            if response.status_code != 200:
                print("Telegram error:", response.text)

        except Exception as e:
            print("Telegram error:", str(e))

    # ----------------------------
    def update(self, data):
        goat_id = data['goat_id']
        self.history[goat_id].append(data)

        alerts = []

        temps = [d['temperature'] for d in self.history[goat_id]]
        moves = [d['movement'] for d in self.history[goat_id]]
        feeds = [d['feed'] for d in self.history[goat_id]]

        if not temps:
            return

        # ----------------------------
        # NEW: Sustained low movement tracking
        # ----------------------------
        if data['movement'] < 3:
            self.low_movement_counter[goat_id] += 1
        else:
            self.low_movement_counter[goat_id] = 0

        # --- 1. Build baseline ---
        if goat_id not in self.baseline and len(self.history[goat_id]) >= self.BASELINE_SIZE:
            self.baseline[goat_id] = {
                "temp": sum(temps) / len(temps),
                "movement": sum(moves) / len(moves),
                "feed": sum(feeds) / len(feeds)
            }
            print(f"Baseline set for {goat_id}")

        # --- 2. Baseline deviation ---
        if goat_id in self.baseline:
            base = self.baseline[goat_id]

            temp_change = (data['temperature'] - base['temp']) / base['temp']
            move_change = (base['movement'] - data['movement']) / base['movement']
            feed_change = (base['feed'] - data['feed']) / base['feed']

            if temp_change > 0.05 and move_change > 0.4 and feed_change > 0.4:
                if self.should_send(goat_id, "baseline_illness"):
                    alerts.append("Possible illness (baseline deviation)")

        # --- 3. High temperature ---
        if data['temperature'] > 40:
            if self.should_send(goat_id, "high_temp"):
                alerts.append("High temperature")

        # --- 4. Combined pattern ---
        if len(temps) >= 20:
            recent_temp = sum(temps[-5:]) / 5
            recent_move = sum(moves[-5:]) / 5
            recent_feed = sum(feeds[-5:]) / 5

            if recent_temp > 39.5 and recent_move < 5 and recent_feed < 200:
                if self.should_send(goat_id, "pattern"):
                    alerts.append("Possible illness detected")

        # ----------------------------
        # NEW: Sustained inactivity alert
        # ----------------------------
        if self.low_movement_counter[goat_id] > 10:
            if self.should_send(goat_id, "sustained_low_movement"):
                alerts.append("Goat inactive for long duration")

        # --- 5. Recovery ---
        if goat_id in self.baseline:
            base = self.baseline[goat_id]

            temp_diff = abs(data['temperature'] - base['temp']) / base['temp']
            move_diff = abs(data['movement'] - base['movement']) / base['movement']
            feed_diff = abs(data['feed'] - base['feed']) / base['feed']

            if self.goat_status.get(goat_id) in ["ALERT", "CRITICAL"]:
                if temp_diff < 0.03 and move_diff < 0.2 and feed_diff < 0.2:
                    if self.should_send(goat_id, "recovery"):
                        alerts.append("Goat recovered")

        # --- 6. Status update ---
        if alerts:
            if any("recovered" in a.lower() for a in alerts):
                self.goat_status[goat_id] = "RECOVERED"
            elif any("illness" in a.lower() for a in alerts):
                self.goat_status[goat_id] = "CRITICAL"
            else:
                self.goat_status[goat_id] = "ALERT"

            self.save_alert(goat_id, alerts)
            self.send_alert(alerts, data)

        elif goat_id not in self.goat_status:
            self.goat_status[goat_id] = "NORMAL"
