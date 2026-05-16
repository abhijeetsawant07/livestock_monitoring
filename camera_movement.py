import cv2
import requests
import time
from collections import deque

# ----------------------------
# Config
# ----------------------------
RTSP_URL = "rtsp://goatmonitor:Im_Monitor@192.168.1.127:554/stream1"
API_URL = "https://livestock-monitoring.onrender.com/sensor-data"

# ----------------------------
# Buffers
# ----------------------------
data_buffer = deque(maxlen=100)
movement_history = deque(maxlen=20)

# ----------------------------
# Camera connect with retry
# ----------------------------
def connect_camera(rtsp_url):
    while True:
        print("🔄 Trying to connect to camera...")
        cap = cv2.VideoCapture(rtsp_url)

        if cap.isOpened():
            print("✅ Camera connected")
            return cap
        else:
            print("❌ Failed to connect. Retrying in 5 seconds...")
            time.sleep(5)

# ----------------------------
# Send data with retry buffer
# ----------------------------
def send_buffered_data():
    while data_buffer:
        try:
            item = data_buffer[0]
            response = requests.post(API_URL, json=item, timeout=5)

            if response.status_code == 200:
                print("📡 Sent:", item)
                data_buffer.popleft()
            else:
                print("❌ API error:", response.status_code)
                break

        except Exception as e:
            print("⚠️ Network issue, retrying later...", e)
            break

# ----------------------------
# Start camera
# ----------------------------
cap = connect_camera(RTSP_URL)

# ----------------------------
# Get first frame safely
# ----------------------------
while True:
    ret, prev_frame = cap.read()
    if ret:
        break
    print("⚠️ Waiting for first frame...")
    time.sleep(1)

prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

last_sent_time = 0

# ----------------------------
# Main loop
# ----------------------------
while True:
    ret, frame = cap.read()

    # --- Camera reconnect ---
    if not ret:
        print("⚠️ Lost camera feed. Reconnecting...")
        cap.release()
        time.sleep(2)
        cap = connect_camera(RTSP_URL)
        continue

    # --- Preprocess ---
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # --- Movement detection ---
    diff = cv2.absdiff(prev_gray, gray)
    _, thresh = cv2.threshold(diff, 15, 255, cv2.THRESH_BINARY)

    # Noise removal
    thresh = cv2.erode(thresh, None, iterations=1)
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Movement score
    movement_score = cv2.countNonZero(thresh)

    if movement_score < 500:
        movement_score = 0

    movement_score = movement_score / 1000

    # --- Smooth movement ---
    movement_history.append(movement_score)
    avg_movement = sum(movement_history) / len(movement_history)

    print(f"Current: {movement_score:.2f}, Avg: {avg_movement:.2f}")

    # --- Send data every 3 sec ---
    current_time = time.time()
    if current_time - last_sent_time > 3:

        data = {
            "goat_id": "goat_1",
            "temperature": 39,
            "movement": int(avg_movement),
            "feed": 300
        }

        # Add to buffer
        data_buffer.append(data)

        # Try sending buffer
        send_buffered_data()

        last_sent_time = current_time

    prev_gray = gray.copy()

    # --- Display ---
    frame = cv2.resize(frame, (640, 480))
    thresh = cv2.resize(thresh, (640, 480))

    cv2.imshow("Camera Feed", frame)
    cv2.imshow("Movement Mask", thresh)

    if cv2.waitKey(1) == 27:
        break

# ----------------------------
# Cleanup
# ----------------------------
cap.release()
cv2.destroyAllWindows()
