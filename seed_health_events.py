from db import get_conn

conn = get_conn()
cur = conn.cursor()

events = [
    (
        "goat_1",
        "status",
        "Bella registered in system"
    ),
    (
        "goat_1",
        "health",
        "Healthy baseline established"
    )
]

cur.executemany("""
INSERT INTO health_events (
    goat_id,
    event_type,
    description
)
VALUES (?, ?, ?)
""", events)

conn.commit()
conn.close()

print("✅ Health events added")
