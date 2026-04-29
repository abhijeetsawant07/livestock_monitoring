from flask import Flask, request, jsonify
import datetime
import os
from db import init_db, get_conn
from alerts import GoatHealthMonitor

# --- Config ---
TOKEN = os.getenv("TELEGRAM_TOKEN") or "8059214847:AAHH5I1Wi34x6wJojqFIwbVX0GlY3r4fD2k"
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or "8442560303"

# --- Initialize monitor ---
monitor = GoatHealthMonitor(TOKEN, CHAT_ID)

app = Flask(__name__)

@app.route('/sensor-data', methods=['POST'])
def receive_data():
    data = request.json
    data['timestamp'] = str(datetime.datetime.now())

    # Save to DB
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO goat_data (goat_id, temperature, movement, feed, timestamp)
    VALUES (?, ?, ?, ?, ?)
    """, (
        data['goat_id'],
        data['temperature'],
        data['movement'],
        data['feed'],
        data['timestamp']
    ))

    conn.commit()
    conn.close()

    # Process alerts
    monitor.update(data)

    return jsonify({"status": "received"})


if __name__ == '__main__':
    init_db()

    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
