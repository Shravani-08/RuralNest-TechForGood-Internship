import sqlite3

conn = sqlite3.connect("ruralnest.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT UNIQUE,
    dob TEXT,
    aadhaar_number TEXT,
    gender TEXT,
    address TEXT,
    blood_group TEXT,
    edd TEXT,
    pregnancy_status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    service TEXT,
    date TEXT,
    time TEXT,
    location TEXT,
    notes TEXT,
    status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS emergencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    user_name TEXT,
    location TEXT,
    message TEXT,
    timestamp TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully.")