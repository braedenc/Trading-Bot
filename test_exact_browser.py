import httpx
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("TWELVE_DATA_KEY")

# Test the exact same endpoint that worked in browser
url = "https://api.twelvedata.com/price"
params = {
    "symbol": "AAPL",
    "apikey": key,
}

print(f"Testing URL: {url}")
print(f"Params: {params}")
print(f"Full URL: {url}?symbol=AAPL&apikey={key[:8]}...")

r = httpx.get(url, params=params)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")
print(f"JSON: {r.json()}") 