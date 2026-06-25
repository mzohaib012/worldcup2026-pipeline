import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("FOOTBALL_DATA_TOKEN")
URL = "https://api.football-data.org/v4/competitions/WC/matches"

headers = {
    "X-Auth-Token": TOKEN
}

response = requests.get(URL, headers=headers)
data = response.json()

print("Status Code:", response.status_code)
print("Total matches found:", len(data.get("matches", [])))

for match in data.get("matches", [])[:3]:
    home = match["homeTeam"]["name"]
    away = match["awayTeam"]["name"]
    date = match["utcDate"]
    status = match["status"]
    print(f"{home} vs {away} | {date} | Status: {status}")

if "message" in data:
    print("Message/Error:", data["message"])