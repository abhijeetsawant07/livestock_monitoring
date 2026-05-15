import cv2
import requests
import time
from collections import deque

movement_history = deque(maxlen=20)

RTSP_URL = "rtsp://goatmonitor:Im_Monitor@192.168.1.127:554/stream1"
API_URL = "https://livestock-monitoring.onrender.com/sensor-data"

cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("...Cannot connect to camera...")
    exit()

print("...Camera connected...")

ret, prev_frame = cap.read()
if not ret:
    print("...Failed to read first frame...")
    exit()

prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

last_sent_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("...Frame error...")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Frame difference
    diff = cv2.absdiff(prev_gray, gray)
    _, thresh = cv2.threshold(diff, 15, 255, cv2.THRESH_BINARY)

    thresh = cv2.erode(thresh, None, iterations=1)
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Remove noise
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Movement score
    movement_score = cv2.countNonZero(thresh)

    if movement_score < 500:
        movement_score = 0

    movement_score = movement_score / 1000

    movement_history.append(movement_score)
    avg_movement = sum(movement_history) / len(movement_history)

    print(f"Current: {movement_score:.2f}, Avg: {avg_movement:.2f}")

    # Send data every 3 seconds ONLY
    current_time = time.time()
    if current_time - last_sent_time > 3:
        data = {
            "goat_id": "goat_1",
            "temperature": 39,
            "movement": int(avg_movement),
            "feed": 300
        }

        try:
            requests.post(API_URL, json=data, timeout=5)
            print("...Sent to backend...")
        except Exception as e:
            print("API error:", e)

        last_sent_time = current_time

    prev_gray = gray.copy()

    # Display
    frame = cv2.resize(frame, (640, 480))
    thresh = cv2.resize(thresh, (640, 480))

    cv2.imshow("Camera Feed", frame)
    cv2.imshow("Movement Mask", thresh)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
