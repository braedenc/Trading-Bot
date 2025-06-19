import pandas as pd
import time
import logging
from datetime import datetime, timezone
from .finnhub_client import FinnhubClient

class MarketDataClient:
    def __init__(self, config, api_keys):
        print("MarketDataClient initialized.")
        self.config = config
        self.api_keys = api_keys
        self.provider = config.get('provider', 'TwelveData') # Default to TwelveData
        self.symbol_providers = config.get("symbol_providers", {})
        self._cache = {}  # {symbol: (latest_timestamp, df)}
        print(f"Market data provider configured: {self.provider}")
        
        # Initialize Finnhub client if API key exists
        if api_keys.get("FINNHUB_API_KEY"):
            self.finnhub_client = FinnhubClient(api_keys["FINNHUB_API_KEY"])
            print("Finnhub client initialized")
        else:
            self.finnhub_client = None
            print("Finnhub API key not found - Finnhub functionality disabled")

    def fetch_price_data(self, symbol):
        """
        Fetches current price data for a given symbol.
        Returns a pandas DataFrame with 'timestamp', 'open', 'high', 'low', 'close', 'volume'.
        Index should be 'timestamp'.
        Uses caching to avoid excessive API calls.
        """
        now = datetime.now(timezone.utc)
        
        # Check cache first
        if symbol in self._cache:
            cached_timestamp, cached_df = self._cache[symbol]
            time_diff = (now - cached_timestamp).seconds
            
            # Return cached data if:
            # 1. Current second is less than 58 (avoiding minute boundary)
            # 2. Cache is less than 59 seconds old
            if now.second < 58 and time_diff < 59:
                logging.debug(f"Cache hit for {symbol}")
                return cached_df
        
        logging.debug(f"Cache miss for {symbol}")
        
        # Get provider for this symbol
        provider = self.symbol_providers.get(symbol, self.provider)
        
        # Auto-detect forex pairs (XXX/YYY format) and use Finnhub
        if "/" in symbol and self.finnhub_client:
            provider = "Finnhub"
            
        print(f"Fetching price data for {symbol} via {provider}...")
        
        # Use Finnhub if specified
        if provider == "Finnhub" and self.finnhub_client:
            df = self.finnhub_client.get_latest_quote(symbol)
            if df is not None:
                self._cache[symbol] = (now, df)
                return df
            logging.warning(f"Failed to get data from Finnhub for {symbol}")
        
        # Fallback to placeholder data for now
        time.sleep(0.1) # Simulate API call latency
        data = {
            'timestamp': [pd.Timestamp.now(tz='UTC')],
            'open': [150.0 + time.time() % 10], # Add some variation
            'high': [151.0 + time.time() % 10],
            'low': [149.0 + time.time() % 10],
            'close': [150.5 + time.time() % 10],
            'volume': [100000 + int(time.time() % 1000)]
        }
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        
        # Update cache
        self._cache[symbol] = (now, df)
        return df

    def get_historical_data(self, symbol, start_date, end_date, interval="1day"):
        print(f"Fetching historical data for {symbol} from {start_date} to {end_date} (interval: {interval}) via {self.provider}")
        # TODO: Implement actual historical data fetching logic
        # Example placeholder structure:
        # columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        # return pd.DataFrame(columns=columns).set_index('timestamp')
        return pd.DataFrame() # Return empty DataFrame as placeholder 