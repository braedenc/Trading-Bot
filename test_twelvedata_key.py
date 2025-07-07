import httpx
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("TWELVE_DATA_KEY")
print(f"Testing key: {key[:8]}...")

# Test 1: Time series endpoint
url1 = "https://api.twelvedata.com/time_series"
params1 = {
    "symbol": "AAPL",
    "interval": "1min",
    "apikey": key,
    "outputsize": 1,
}
print("\n1. Testing time_series endpoint:")
r1 = httpx.get(url1, params=params1)
print(f"Status: {r1.status_code}")
print(f"Response: {r1.json()}")

# Test 2: Quote endpoint
url2 = "https://api.twelvedata.com/quote"
params2 = {
    "symbol": "AAPL",
    "apikey": key,
}
print("\n2. Testing quote endpoint:")
r2 = httpx.get(url2, params=params2)
print(f"Status: {r2.status_code}")
print(f"Response: {r2.json()}")

# Test 3: Price endpoint
url3 = "https://api.twelvedata.com/price"
params3 = {
    "symbol": "AAPL",
    "apikey": key,
}
print("\n3. Testing price endpoint:")
r3 = httpx.get(url3, params=params3)
print(f"Status: {r3.status_code}")
print(f"Response: {r3.json()}") 