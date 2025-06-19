import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=dotenv_path, override=True)

# Get API key
key = os.getenv("FINNHUB_API_KEY")
print("\nFinnhub API Key:", key[:6] + "..." if key else "None")

# Test different forex symbol formats
symbols = [
    "OANDA:EUR_USD",
    "FX:EURUSD",
    "EURUSD",
    "EUR/USD"
]

for symbol in symbols:
    print(f"\nTesting Finnhub API for {symbol}...")
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={key}"
    
    try:
        resp = requests.get(url, timeout=10)
        print(f"HTTP Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("c"):  # Check if we got a valid price
                print("\nSuccess! Got valid price data:")
                print(f"Current Price: {data['c']}")
                print(f"Open: {data['o']}")
                print(f"High: {data['h']}")
                print(f"Low: {data['l']}")
                break  # Stop if we get valid data
            else:
                print("No price data in response")
        else:
            print("API request failed")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print("-" * 50) 