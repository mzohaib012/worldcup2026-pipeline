import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("FOOTBALL_DATA_TOKEN")
url = "https://api.football-data.org/v4/competitions/WC/matches"
headers = {"X-Auth-Token": TOKEN}
resp = requests.get(url, headers=headers, params={"dateFrom": "2026-06-12", "dateTo": "2026-06-12"})
data = resp.json()
print(json.dumps(data["matches"][0], indent=2))