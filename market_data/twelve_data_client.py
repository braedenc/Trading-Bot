"""
TwelveData API client for fetching market data.
Provides methods to retrieve real-time and historical price data.
"""

import os
import requests
import pandas as pd
import logging


class TwelveDataClient:
    """
    Client for interacting with the TwelveData API to fetch market data.
    
    Attributes:
        api_key (str): API key for authenticating with TwelveData
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the TwelveData client.
        
        Args:
            api_key (str): API key for TwelveData authentication
            
        Raises:
            RuntimeError: If api_key is None or empty
        """
        if not api_key or api_key == "test_key":
            error_msg = "TWELVE_DATA_API_KEY missing—check .env"
            logging.error(error_msg)
            raise RuntimeError(error_msg)
        self.api_key = api_key

    def get_latest_bar(self, symbol: str, interval="1min") -> pd.DataFrame | None:
        """
        Fetch the latest price bar for a given symbol.
        
        Args:
            symbol (str): The trading symbol to fetch data for
            interval (str, optional): The time interval for the bar. Defaults to "1min".
            
        Returns:
            pd.DataFrame | None: DataFrame containing the latest bar data with columns:
                - timestamp (index): Datetime of the bar
                - open: Opening price
                - high: Highest price
                - low: Lowest price
                - close: Closing price
                - volume: Trading volume
            Returns None if there was an error fetching the data.
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = (
            "https://api.twelvedata.com/time_series"
            f"?symbol={symbol}&interval={interval}&limit=1&apikey={self.api_key}"
        )
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            print("TwelveData HTTP error:", resp.status_code, resp.text)
            return None
            
        resp.raise_for_status()
        d = resp.json()
        if d.get("status") == "error":
            print("TwelveData API error:", d.get("message"))
            return None
            
        values = d["values"][0]
        df = pd.DataFrame([{
            "timestamp": pd.to_datetime(values["datetime"]),
            "open": float(values["open"]),
            "high": float(values["high"]),
            "low":  float(values["low"]),
            "close":float(values["close"]),
            "volume": float(values.get("volume", 0))  # default to 0 when not provided
        }]).set_index("timestamp")
        return df 