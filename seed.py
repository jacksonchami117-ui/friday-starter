import os
import csv

# Figure out where your state/uploads folder is
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "state", "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

CSV_PATH = os.path.join(UPLOADS_DIR, "leads.csv")

# Sample test leads
rows = [
    ["Business", "First Name", "Last Name", "Email", "Address", "Phone Number", "Website"],
    ["Art Beins Karate", "Larry", "Beins", "larry@abkusa.com", "123 Main St, Howell, NJ", "17323634300", "abkusa.com"],
    ["Test Martial Arts", "Jane", "Doe", "jane@testma.com", "456 Oak Ave, Freehold, NJ", "17325554444", "testma.com"],
    ["Kickboxing World", "Mike", "Smith", "mike@kbworld.com", "789 Pine Rd, Jackson, NJ", "17327778888", "kbworld.com"],
]

with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print(f"✅ Seed data written to {CSV_PATH}")