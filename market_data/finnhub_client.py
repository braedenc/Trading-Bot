import os, requests, pandas as pd, datetime as dt

class FinnhubClient:
    def __init__(self, api_key:str):
        self.key = api_key
        
    def get_latest_quote(self, symbol:str) -> pd.DataFrame|None:
        # Convert forex pairs to Finnhub format (e.g., EUR/USD -> OANDA:EUR_USD)
        if "/" in symbol:
            base, quote = symbol.split("/")
            symbol = f"OANDA:{base}_{quote}"
            
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={self.key}"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        q = r.json()
        if not q.get("c"):
            return None
        ts = dt.datetime.utcnow()
        df = pd.DataFrame([{
            "timestamp": ts,
            "open": q["o"],
            "high": max(q["o"], q["h"], q["c"]),
            "low":  min(q["o"], q["l"], q["c"]),
            "close":q["c"],
            "volume": q.get("v", 0),
        }]).set_index("timestamp")
        return df 