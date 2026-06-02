from db import get_conn

conn = get_conn()
cur = conn.cursor()

cur.execute("""
INSERT OR IGNORE INTO goats (
    goat_id,
    name,
    breed,
    age,
    weight,
    gender
)
VALUES (
    'goat_1',
    'Bella',
    'Boer',
    2,
    45,
    'Female'
)
""")

conn.commit()
conn.close()

print("----Bella added----")
