import json
import math
import numpy as np
import pandas as pd
from langchain_core.messages import HumanMessage

from src.agents.technicals import (
    BaseAgent,
    AgentState,
    get_prices,
    prices_to_df,
    safe_float,
    normalize_pandas,
    weighted_signal_combination,
    calculate_hurst_exponent,
    calculate_atr,
    calculate_adx,
    show_agent_reasoning
)
from src.utils.progress import progress


class OptimizedTechnicalAgent(BaseAgent):
    """
    Optimized technical analysis agent with improved performance for SMA calculations.
    
    Key optimizations:
    1. Pre-calculate all rolling windows at once
    2. Use vectorized operations where possible
    3. Cache intermediate calculations
    4. Reduce redundant calculations
    """
    
    def __init__(self):
        super().__init__()
        self._cache = {}
    
    def technical_analyst_agent(self, state: AgentState):
        """
        Optimized technical analysis system that combines multiple trading strategies.
        """
        data = state["data"]
        start_date = data["start_date"]
        end_date = data["end_date"]
        tickers = data["tickers"]
        
        # Initialize analysis for each ticker
        technical_analysis = {}
        
        for ticker in tickers:
            progress.update_status("technical_analyst_agent", ticker, "Analyzing price data")
            
            # Get the historical price data
            prices = get_prices(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
            )
            
            if not prices:
                progress.update_status("technical_analyst_agent", ticker, "Failed: No price data found")
                continue
            
            # Convert prices to a DataFrame
            prices_df = prices_to_df(prices)
            
            # Pre-calculate all needed data at once for better performance
            progress.update_status("technical_analyst_agent", ticker, "Pre-calculating indicators")
            indicators = self._pre_calculate_indicators(prices_df)
            
            progress.update_status("technical_analyst_agent", ticker, "Calculating signals")
            
            # Use pre-calculated indicators for all signal calculations
            trend_signals = self._calculate_trend_signals_optimized(prices_df, indicators)
            mean_reversion_signals = self._calculate_mean_reversion_signals_optimized(prices_df, indicators)
            momentum_signals = self._calculate_momentum_signals_optimized(prices_df, indicators)
            volatility_signals = self._calculate_volatility_signals_optimized(prices_df, indicators)
            stat_arb_signals = self._calculate_stat_arb_signals_optimized(prices_df, indicators)
            
            # Combine all signals using a weighted ensemble approach
            strategy_weights = {
                "trend": 0.25,
                "mean_reversion": 0.20,
                "momentum": 0.25,
                "volatility": 0.15,
                "stat_arb": 0.15,
            }
            
            progress.update_status("technical_analyst_agent", ticker, "Combining signals")
            combined_signal = weighted_signal_combination(
                {
                    "trend": trend_signals,
                    "mean_reversion": mean_reversion_signals,
                    "momentum": momentum_signals,
                    "volatility": volatility_signals,
                    "stat_arb": stat_arb_signals,
                },
                strategy_weights,
            )
            
            # Generate detailed analysis report for this ticker
            technical_analysis[ticker] = {
                "signal": combined_signal["signal"],
                "confidence": round(combined_signal["confidence"] * 100),
                "reasoning": {
                    "trend_following": {
                        "signal": trend_signals["signal"],
                        "confidence": round(trend_signals["confidence"] * 100),
                        "metrics": normalize_pandas(trend_signals["metrics"]),
                    },
                    "mean_reversion": {
                        "signal": mean_reversion_signals["signal"],
                        "confidence": round(mean_reversion_signals["confidence"] * 100),
                        "metrics": normalize_pandas(mean_reversion_signals["metrics"]),
                    },
                    "momentum": {
                        "signal": momentum_signals["signal"],
                        "confidence": round(momentum_signals["confidence"] * 100),
                        "metrics": normalize_pandas(momentum_signals["metrics"]),
                    },
                    "volatility": {
                        "signal": volatility_signals["signal"],
                        "confidence": round(volatility_signals["confidence"] * 100),
                        "metrics": normalize_pandas(volatility_signals["metrics"]),
                    },
                    "statistical_arbitrage": {
                        "signal": stat_arb_signals["signal"],
                        "confidence": round(stat_arb_signals["confidence"] * 100),
                        "metrics": normalize_pandas(stat_arb_signals["metrics"]),
                    },
                },
            }
            progress.update_status("technical_analyst_agent", ticker, "Done", analysis=json.dumps(technical_analysis, indent=4))
        
        # Create the technical analyst message
        message = HumanMessage(
            content=json.dumps(technical_analysis),
            name="technical_analyst_agent",
        )
        
        if state["metadata"]["show_reasoning"]:
            show_agent_reasoning(technical_analysis, "Technical Analyst")
        
        # Add the signal to the analyst_signals list
        state["data"]["analyst_signals"]["technical_analyst_agent"] = technical_analysis
        
        progress.update_status("technical_analyst_agent", None, "Done")
        
        return {
            "messages": state["messages"] + [message],
            "data": data,
        }
    
    def _pre_calculate_indicators(self, prices_df):
        """
        Pre-calculate all indicators at once to improve performance.
        This avoids redundant calculations and uses vectorized operations.
        """
        indicators = {}
        
        # Price data
        close = prices_df["close"]
        high = prices_df["high"]
        low = prices_df["low"]
        volume = prices_df["volume"]
        
        # Returns
        returns = close.pct_change()
        indicators["returns"] = returns
        
        # EMAs - calculate all at once
        indicators["ema_8"] = close.ewm(span=8, adjust=False).mean()
        indicators["ema_21"] = close.ewm(span=21, adjust=False).mean()
        indicators["ema_55"] = close.ewm(span=55, adjust=False).mean()
        
        # SMAs and standard deviations - calculate all at once
        indicators["sma_20"] = close.rolling(20).mean()
        indicators["sma_50"] = close.rolling(50).mean()
        indicators["std_20"] = close.rolling(20).std()
        indicators["std_50"] = close.rolling(50).std()
        
        # Momentum calculations - vectorized
        indicators["mom_1m"] = returns.rolling(21).sum()
        indicators["mom_3m"] = returns.rolling(63).sum()
        indicators["mom_6m"] = returns.rolling(126).sum()
        
        # Volume calculations
        indicators["volume_ma_21"] = volume.rolling(21).mean()
        
        # Volatility calculations
        indicators["hist_vol_21"] = returns.rolling(21).std() * math.sqrt(252)
        indicators["hist_vol_63_ma"] = indicators["hist_vol_21"].rolling(63).mean()
        indicators["hist_vol_63_std"] = indicators["hist_vol_21"].rolling(63).std()
        
        # Statistical calculations
        indicators["skew_63"] = returns.rolling(63).skew()
        indicators["kurt_63"] = returns.rolling(63).kurt()
        
        # RSI calculations - optimized
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        indicators["rsi_14"] = self._calculate_rsi_optimized(gain, loss, 14)
        indicators["rsi_28"] = self._calculate_rsi_optimized(gain, loss, 28)
        
        # ADX calculation
        indicators["adx_data"] = calculate_adx(prices_df, 14)
        
        # ATR calculation
        indicators["atr"] = calculate_atr(prices_df, 14)
        
        return indicators
    
    def _calculate_rsi_optimized(self, gain, loss, period):
        """Optimized RSI calculation using exponential moving average."""
        avg_gain = gain.ewm(com=period-1, adjust=True, min_periods=period).mean()
        avg_loss = loss.ewm(com=period-1, adjust=True, min_periods=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_trend_signals_optimized(self, prices_df, indicators):
        """Optimized trend following strategy using pre-calculated indicators."""
        # Use pre-calculated EMAs
        ema_8 = indicators["ema_8"]
        ema_21 = indicators["ema_21"]
        ema_55 = indicators["ema_55"]
        
        # Use pre-calculated ADX
        adx = indicators["adx_data"]["adx"].iloc[-1]
        
        # Determine trend direction and strength
        short_trend = ema_8.iloc[-1] > ema_21.iloc[-1]
        medium_trend = ema_21.iloc[-1] > ema_55.iloc[-1]
        
        # Combine signals with confidence weighting
        trend_strength = adx / 100.0
        
        if short_trend and medium_trend:
            signal = "bullish"
            confidence = trend_strength
        elif not short_trend and not medium_trend:
            signal = "bearish"
            confidence = trend_strength
        else:
            signal = "neutral"
            confidence = 0.5
        
        return {
            "signal": signal,
            "confidence": confidence,
            "metrics": {
                "adx": safe_float(adx),
                "trend_strength": safe_float(trend_strength),
            },
        }
    
    def _calculate_mean_reversion_signals_optimized(self, prices_df, indicators):
        """Optimized mean reversion strategy using pre-calculated indicators."""
        close = prices_df["close"]
        
        # Use pre-calculated values
        ma_50 = indicators["sma_50"]
        std_50 = indicators["std_50"]
        
        # Z-score calculation
        z_score = (close - ma_50) / std_50
        
        # Bollinger Bands using pre-calculated values
        sma_20 = indicators["sma_20"]
        std_20 = indicators["std_20"]
        bb_upper = sma_20 + (std_20 * 2)
        bb_lower = sma_20 - (std_20 * 2)
        
        # Use pre-calculated RSI
        rsi_14 = indicators["rsi_14"]
        rsi_28 = indicators["rsi_28"]
        
        # Mean reversion signals
        price_vs_bb = (close.iloc[-1] - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])
        
        # Combine signals
        if z_score.iloc[-1] < -2 and price_vs_bb < 0.2:
            signal = "bullish"
            confidence = min(abs(z_score.iloc[-1]) / 4, 1.0)
        elif z_score.iloc[-1] > 2 and price_vs_bb > 0.8:
            signal = "bearish"
            confidence = min(abs(z_score.iloc[-1]) / 4, 1.0)
        else:
            signal = "neutral"
            confidence = 0.5
        
        return {
            "signal": signal,
            "confidence": confidence,
            "metrics": {
                "z_score": safe_float(z_score.iloc[-1]),
                "price_vs_bb": safe_float(price_vs_bb),
                "rsi_14": safe_float(rsi_14.iloc[-1]),
                "rsi_28": safe_float(rsi_28.iloc[-1]),
            },
        }
    
    def _calculate_momentum_signals_optimized(self, prices_df, indicators):
        """Optimized momentum strategy using pre-calculated indicators."""
        # Use pre-calculated momentum values
        mom_1m = indicators["mom_1m"]
        mom_3m = indicators["mom_3m"]
        mom_6m = indicators["mom_6m"]
        
        # Volume momentum
        volume = prices_df["volume"]
        volume_ma = indicators["volume_ma_21"]
        volume_momentum = volume.iloc[-1] / volume_ma.iloc[-1] if volume_ma.iloc[-1] > 0 else 1.0
        
        # Calculate momentum score
        momentum_score = (0.4 * mom_1m.iloc[-1] + 0.3 * mom_3m.iloc[-1] + 0.3 * mom_6m.iloc[-1])
        
        # Volume confirmation
        volume_confirmation = volume_momentum > 1.0
        
        if momentum_score > 0.05 and volume_confirmation:
            signal = "bullish"
            confidence = min(abs(momentum_score) * 5, 1.0)
        elif momentum_score < -0.05 and volume_confirmation:
            signal = "bearish"
            confidence = min(abs(momentum_score) * 5, 1.0)
        else:
            signal = "neutral"
            confidence = 0.5
        
        return {
            "signal": signal,
            "confidence": confidence,
            "metrics": {
                "momentum_1m": safe_float(mom_1m.iloc[-1]),
                "momentum_3m": safe_float(mom_3m.iloc[-1]),
                "momentum_6m": safe_float(mom_6m.iloc[-1]),
                "volume_momentum": safe_float(volume_momentum),
            },
        }
    
    def _calculate_volatility_signals_optimized(self, prices_df, indicators):
        """Optimized volatility-based trading strategy using pre-calculated indicators."""
        # Use pre-calculated volatility metrics
        hist_vol = indicators["hist_vol_21"]
        vol_ma = indicators["hist_vol_63_ma"]
        vol_std = indicators["hist_vol_63_std"]
        
        # Volatility regime detection
        vol_regime = hist_vol.iloc[-1] / vol_ma.iloc[-1] if vol_ma.iloc[-1] > 0 else 1.0
        
        # Volatility z-score
        vol_z_score = ((hist_vol.iloc[-1] - vol_ma.iloc[-1]) / vol_std.iloc[-1] 
                       if vol_std.iloc[-1] > 0 else 0.0)
        
        # ATR ratio
        atr = indicators["atr"]
        atr_ratio = atr.iloc[-1] / prices_df["close"].iloc[-1] if prices_df["close"].iloc[-1] > 0 else 0.0
        
        # Generate signal based on volatility regime
        if vol_regime < 0.8 and vol_z_score < -1:
            signal = "bullish"  # Low vol regime, potential for expansion
            confidence = min(abs(vol_z_score) / 3, 1.0)
        elif vol_regime > 1.2 and vol_z_score > 1:
            signal = "bearish"  # High vol regime, potential for contraction
            confidence = min(abs(vol_z_score) / 3, 1.0)
        else:
            signal = "neutral"
            confidence = 0.5
        
        return {
            "signal": signal,
            "confidence": confidence,
            "metrics": {
                "historical_volatility": safe_float(hist_vol.iloc[-1]),
                "volatility_regime": safe_float(vol_regime),
                "volatility_z_score": safe_float(vol_z_score),
                "atr_ratio": safe_float(atr_ratio),
            },
        }
    
    def _calculate_stat_arb_signals_optimized(self, prices_df, indicators):
        """Optimized statistical arbitrage signals using pre-calculated indicators."""
        # Use pre-calculated statistics
        skew = indicators["skew_63"]
        kurt = indicators["kurt_63"]
        
        # Calculate Hurst exponent (this is still expensive, but necessary)
        hurst = calculate_hurst_exponent(prices_df["close"])
        
        # Generate signal based on statistical properties
        if hurst < 0.4 and skew.iloc[-1] > 1:
            signal = "bullish"
            confidence = (0.5 - hurst) * 2
        elif hurst < 0.4 and skew.iloc[-1] < -1:
            signal = "bearish"
            confidence = (0.5 - hurst) * 2
        else:
            signal = "neutral"
            confidence = 0.5
        
        return {
            "signal": signal,
            "confidence": confidence,
            "metrics": {
                "hurst_exponent": safe_float(hurst),
                "skewness": safe_float(skew.iloc[-1]),
                "kurtosis": safe_float(kurt.iloc[-1]),
            },
        }