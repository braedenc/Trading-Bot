import os
import sys
from dotenv import load_dotenv
import pathlib

# Clear any existing environment variables
if 'TWELVE_DATA_KEY' in os.environ:
    del os.environ['TWELVE_DATA_KEY']

# Load fresh from .env
project_root = pathlib.Path(__file__).resolve().parent
load_dotenv(dotenv_path=project_root / ".env")

key = os.getenv("TWELVE_DATA_KEY")
print(f"Fresh key: {key}")
print(f"Key ends with: {key[-5:] if key else 'None'}")

# Test the API
import httpx
url = "https://api.twelvedata.com/price"
params = {"symbol": "AAPL", "apikey": key}
r = httpx.get(url, params=params)
print(f"API Response: {r.json()}") 