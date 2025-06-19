import os
import sys
import time
import logging
import yaml
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv
from pathlib import Path

print("Starting script...")
import yaml
print("Imported yaml")
import os
print("Imported os")
from dotenv import load_dotenv
print("Imported dotenv")
import importlib
print("Imported importlib")
import time
print("Imported time")
import logging
print("Imported logging")
import pandas as pd # For type hinting and creating empty DataFrame for strategy if needed
print("Imported pandas")
import traceback
print("Imported traceback")
from portfolio.risk_manager import RiskManager
print("Imported RiskManager")
import numpy as np
print("Imported numpy")
from pathlib import Path

print("TD key in env =>", os.getenv("TWELVE_DATA_API_KEY"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables from .env file
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=dotenv_path, override=True)
logging.info("Loaded .env ➜ %s", dotenv_path)

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'src'))

# --- Helper Functions ---

def load_configuration(config_path="config.yaml"):
    """Loads the YAML configuration file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print(f"Configuration loaded successfully from {config_path}.")
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML configuration: {e}")
        return None

def setup_logging(log_config):
    """Sets up logging based on configuration."""
    log_level_str = log_config.get('level', 'INFO').upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    # Always log to console for debugging
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
    print(f"Logging configured. Level: {log_level_str}")

def load_strategy_class(strategy_name):
    """Dynamically loads a strategy class."""
    print(f"Attempting to load strategy: {strategy_name}")
    try:
        module_name_part = strategy_name.replace('Strategy', '').lower()
        if not module_name_part:
            module_name_part = strategy_name.lower()
        
        module_filename = f"{module_name_part}_strategy"
        module_path = f"strategies.{module_filename}"
        
        print(f"Loading module: {module_path}")
        print(f"Python path: {sys.path}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Looking for file: {os.path.join(os.getcwd(), 'strategies', f'{module_filename}.py')}")
        
        strategy_module = importlib.import_module(module_path)
        StrategyClass = getattr(strategy_module, strategy_name)
        print(f"Successfully loaded strategy class: {strategy_name}")
        return StrategyClass
    except Exception as e:
        print(f"Error loading strategy '{strategy_name}': {str(e)}")
        print(traceback.format_exc())
        return None

def calculate_atr(data: pd.DataFrame, period: int = 14) -> float:
    """
    Calculate Average True Range (ATR) for position sizing.
    
    Args:
        data (pd.DataFrame): Price data with high, low, close columns
        period (int): ATR calculation period
        
    Returns:
        float: Current ATR value
    """
    high = data['high']
    low = data['low']
    close = data['close']
    
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean().iloc[-1]
    
    return atr

# --- Main Application Logic ---

def main():
    print("\n=== Starting Main Function ===")
    
    # Load environment variables
    print("\nLoading environment variables...")
    env_path = ".env"
    if not os.path.exists(env_path):
        print(f"Warning: '{env_path}' not found. Using placeholder values.")
    load_dotenv(dotenv_path=env_path, override=True)
    
    api_keys = {
        "TWELVE_DATA_API_KEY": os.getenv("TWELVE_DATA_API_KEY", "test_key"),
        "FINNHUB_API_KEY": os.getenv("FINNHUB_API_KEY", "test_key"),
        "IBKR_USERNAME": os.getenv("IBKR_USERNAME", "test_user"),
        "IBKR_PASSWORD": os.getenv("IBKR_PASSWORD", "test_pass"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "test_key")
    }
    print("Environment variables loaded")

    # Load configuration
    print("\nLoading configuration...")
    config = load_configuration("config.yaml")
    if not config:
        print("Exiting due to configuration load failure.")
        return

    # Initialize Risk Manager
    print("\nInitializing risk manager...")
    risk_manager = RiskManager(config.get("risk", {}))
    print("Risk manager initialized")

    # Setup logging
    print("\nSetting up logging...")
    setup_logging(config.get('log', {}))
    
    print("\nInitializing components...")
    
    # Initialize Broker
    print("\nInitializing broker...")
    broker_config = config.get('broker', {})
    try:
        start_time = time.time()
        broker_module = importlib.import_module("broker.ibkr_broker")
        IBKRBrokerClass = getattr(broker_module, "IBKRBroker")
        broker = IBKRBrokerClass(config=broker_config, api_keys=api_keys)
        print(f"Broker initialized in {time.time() - start_time:.2f} seconds")
    except Exception as e:
        print(f"Failed to initialize broker: {str(e)}")
        print(traceback.format_exc())
        return

    # Initialize Market Data Client
    print("\nInitializing market data client...")
    market_data_config = config.get('data', {})
    try:
        start_time = time.time()
        market_data_module = importlib.import_module("market_data.market_data_client")
        MarketDataClientClass = getattr(market_data_module, "MarketDataClient")
        market_data_client = MarketDataClientClass(config=market_data_config, api_keys=api_keys)
        print(f"Market data client initialized in {time.time() - start_time:.2f} seconds")
    except Exception as e:
        print(f"Failed to initialize market data client: {str(e)}")
        print(traceback.format_exc())
        return

    # Initialize Strategy
    print("\nInitializing strategy...")
    strategy_config = config.get('strategy', {})
    strategy_name_from_config = strategy_config.get('name')
    strategy_params_from_config = strategy_config.get('params', {})
    
    if not strategy_name_from_config:
        print("Strategy name not found in config.yaml. Exiting.")
        return

    start_time = time.time()
    StrategyClass = load_strategy_class(strategy_name_from_config)
    if not StrategyClass:
        print(f"Failed to load strategy class: {strategy_name_from_config}. Exiting.")
        return
    
    common_configs_for_strategy = {
        'main_config': config,
        'data_config': market_data_config, 
        'broker_config': broker_config
    }
    strategy_instance = StrategyClass(strategy_config=strategy_params_from_config, common_config=common_configs_for_strategy)
    # Set the broker in the strategy for position checking
    if hasattr(strategy_instance, 'set_broker'):
        strategy_instance.set_broker(broker)
    print(f"Strategy initialized in {time.time() - start_time:.2f} seconds")

    symbols = market_data_config.get('symbols', [])
    symbol_queue = symbols.copy()
    if not symbols:
        print("Warning: No symbols found in config.data.symbols")

    # Get initial capital from broker
    try:
        print("Fetching account summary...")
        start_time = time.time()
        account_summary = broker.get_account_summary()
        initial_capital = float(account_summary.get('NetLiquidation', 100000))  # Default to 100k if not available
        print(f"Initial capital: ${initial_capital:,.2f} (fetched in {time.time() - start_time:.2f} seconds)")
    except Exception as e:
        print(f"Warning: Could not get account summary. Using default capital. Error: {e}")
        initial_capital = 100000  # Default capital

    # Main trading loop
    print("\nStarting main trading loop...")
    try:
        bot_cfg = config.get("bot", {})
        max_iters = bot_cfg.get("max_iterations", 0)   # 0 = infinite
        loop_interval = bot_cfg.get("loop_interval_seconds", 60)
        max_reconnect_attempts = 3
        reconnect_delay = 5  # seconds
        
        iteration = 0
        while True:
            print(f"\nIteration {iteration + 1}" + (f" of {max_iters}" if max_iters else ""))
            
            # Check broker connection and attempt reconnect if needed
            if not broker.ib or not broker.ib.isConnected():
                print("Broker disconnected. Attempting to reconnect...")
                reconnect_attempts = 0
                while reconnect_attempts < max_reconnect_attempts:
                    try:
                        broker.connect()
                        print("Successfully reconnected to broker")
                        break
                    except Exception as e:
                        reconnect_attempts += 1
                        print(f"Reconnection attempt {reconnect_attempts} failed: {str(e)}")
                        if reconnect_attempts < max_reconnect_attempts:
                            print(f"Waiting {reconnect_delay} seconds before next attempt...")
                            time.sleep(reconnect_delay)
                        else:
                            print("Max reconnection attempts reached. Exiting...")
                            return
            
            if not symbol_queue:
                symbol_queue = symbols.copy()
            symbol = symbol_queue.pop(0)
            
            print(f"\nProcessing {symbol}...")
            try:
                print("Fetching price data...")
                start_time = time.time()
                current_data = market_data_client.fetch_price_data(symbol)
                fetch_time = time.time() - start_time
                print(f"Price data fetched in {fetch_time:.2f} seconds")
                
                if current_data is None or current_data.empty:
                    print(f"No data received for {symbol}")
                    continue

                # --- basic ATR calculation (1-period True Range) ---
                if {"high", "low", "close"}.issubset(current_data.columns):
                    hl = current_data["high"].iloc[-1] - current_data["low"].iloc[-1]
                    hc = abs(current_data["high"].iloc[-1] - current_data["close"].shift(1).iloc[-1] if len(current_data) > 1 else 0)
                    lc = abs(current_data["low"].iloc[-1]  - current_data["close"].shift(1).iloc[-1] if len(current_data) > 1 else 0)
                    atr = float(np.nanmax([hl, hc, lc]))
                else:
                    atr = current_data["close"].iloc[-1] * 0.001  # fallback 0.1% of price

                # Set the symbol name for position checking in the strategy
                current_data.name = symbol

                print("Generating signal...")
                signal = strategy_instance.generate_signals(current_data)
                print(f"Signal generated: {signal}")

                if signal and signal.lower() != "hold":
                    # Placeholder capital; later read from portfolio module
                    capital = config.get("portfolio", {}).get("initial_capital", 100000)
                    price = current_data["close"].iloc[-1]
                    quantity = risk_manager.position_size(capital, atr, price)
                    if quantity > 0:
                        print(f"Executing {signal.upper()} order for {quantity} of {symbol}")
                        broker.execute_signal(symbol, signal.lower(), quantity)
                        logging.info(f"TRADE_ACTION: Symbol={symbol}, Signal={signal.upper()}, Qty={quantity}, ATR={atr:.4f}")
                    else:
                        logging.warning(f"RiskManager returned qty 0 for {symbol}; skipping trade.")
                else:
                    print(f"No action needed for {symbol} (signal: {signal})")
            
            except Exception as e:
                print(f"Error processing {symbol}: {str(e)}")
                print(traceback.format_exc())
                continue

            iteration += 1
            if max_iters and iteration >= max_iters:
                logging.info("Reached max_iterations. Shutting down.")
                break
                
            print(f"\nCompleted iteration {iteration}")
            if iteration < max_iters or not max_iters:
                print(f"Sleeping for {loop_interval} seconds before next iteration...")
                time.sleep(loop_interval)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Shutting down...")
    except Exception as e:
        print(f"\nUnexpected error in main loop: {str(e)}")
        print(traceback.format_exc())
    finally:
        print("\nShutting down...")
        try:
            broker.disconnect()
            print("Disconnecting from IBKR...")
        except:
            pass
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
 