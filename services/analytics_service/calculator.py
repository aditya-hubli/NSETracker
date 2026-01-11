"""Technical analysis calculator using ta library and custom calculations."""
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Tuple

import ta
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange

from .models import (
    TechnicalIndicators,
    TradingSignal,
    SignalType,
    VolumeAnalysis,
    VolatilityMetrics,
    PatternRecognition,
    PricePattern,
    TimeFrame,
)


class TechnicalAnalyzer:
    """Calculate technical indicators and generate trading signals."""
    
    def __init__(self):
        pass
    
    def get_stock_data(
        self,
        symbol: str,
        period: str = "1y"
    ) -> Optional[pd.DataFrame]:
        """Fetch historical stock data."""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty:
                return None
            
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def calculate_indicators(
        self,
        symbol: str,
        df: Optional[pd.DataFrame] = None
    ) -> Optional[TechnicalIndicators]:
        """Calculate all technical indicators."""
        if df is None:
            df = self.get_stock_data(symbol)
        
        if df is None or df.empty:
            return None
        
        try:
            close = df['Close']
            high = df['High']
            low = df['Low']
            volume = df['Volume']
            
            # Current price
            current_price = float(close.iloc[-1])
            
            # Moving Averages
            sma_20 = SMAIndicator(close, window=20).sma_indicator()
            sma_50 = SMAIndicator(close, window=50).sma_indicator()
            sma_200 = SMAIndicator(close, window=200).sma_indicator()
            ema_12 = EMAIndicator(close, window=12).ema_indicator()
            ema_26 = EMAIndicator(close, window=26).ema_indicator()
            
            # MACD
            macd_indicator = MACD(close)
            macd = macd_indicator.macd()
            macd_signal = macd_indicator.macd_signal()
            macd_diff = macd_indicator.macd_diff()
            
            # RSI
            rsi = RSIIndicator(close, window=14).rsi()
            
            # Bollinger Bands
            bb = BollingerBands(close, window=20, window_dev=2)
            bb_upper = bb.bollinger_hband()
            bb_middle = bb.bollinger_mavg()
            bb_lower = bb.bollinger_lband()
            bb_width = (bb_upper - bb_lower) / bb_middle * 100
            
            # Volume
            volume_sma = volume.rolling(window=20).mean()
            volume_ratio = volume.iloc[-1] / volume_sma.iloc[-1] if volume_sma.iloc[-1] > 0 else 0
            
            # ATR (Average True Range)
            atr = AverageTrueRange(high, low, close, window=14).average_true_range()
            
            # Historical Volatility (annualized)
            returns = close.pct_change().dropna()
            hist_volatility = returns.std() * np.sqrt(252) * 100  # Annualized
            
            # Support/Resistance (simple version - recent lows/highs)
            recent_30d = df.tail(30)
            support = float(recent_30d['Low'].min())
            resistance = float(recent_30d['High'].max())
            
            return TechnicalIndicators(
                symbol=symbol,
                current_price=current_price,
                sma_20=float(sma_20.iloc[-1]) if not pd.isna(sma_20.iloc[-1]) else None,
                sma_50=float(sma_50.iloc[-1]) if not pd.isna(sma_50.iloc[-1]) else None,
                sma_200=float(sma_200.iloc[-1]) if not pd.isna(sma_200.iloc[-1]) else None,
                ema_12=float(ema_12.iloc[-1]) if not pd.isna(ema_12.iloc[-1]) else None,
                ema_26=float(ema_26.iloc[-1]) if not pd.isna(ema_26.iloc[-1]) else None,
                macd=float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else None,
                macd_signal=float(macd_signal.iloc[-1]) if not pd.isna(macd_signal.iloc[-1]) else None,
                macd_histogram=float(macd_diff.iloc[-1]) if not pd.isna(macd_diff.iloc[-1]) else None,
                rsi_14=float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None,
                bb_upper=float(bb_upper.iloc[-1]) if not pd.isna(bb_upper.iloc[-1]) else None,
                bb_middle=float(bb_middle.iloc[-1]) if not pd.isna(bb_middle.iloc[-1]) else None,
                bb_lower=float(bb_lower.iloc[-1]) if not pd.isna(bb_lower.iloc[-1]) else None,
                bb_width=float(bb_width.iloc[-1]) if not pd.isna(bb_width.iloc[-1]) else None,
                volume_sma_20=float(volume_sma.iloc[-1]) if not pd.isna(volume_sma.iloc[-1]) else None,
                volume_ratio=float(volume_ratio) if not pd.isna(volume_ratio) else None,
                atr_14=float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else None,
                historical_volatility=float(hist_volatility) if not pd.isna(hist_volatility) else None,
                support_level=support,
                resistance_level=resistance,
            )
        
        except Exception as e:
            print(f"Error calculating indicators for {symbol}: {e}")
            return None
    
    def generate_signal(
        self,
        symbol: str,
        indicators: TechnicalIndicators,
        df: Optional[pd.DataFrame] = None
    ) -> TradingSignal:
        """Generate trading signal based on indicators."""
        if df is None:
            df = self.get_stock_data(symbol)
        
        buy_signals = 0
        sell_signals = 0
        reasons = []
        total_checks = 0
        
        current_price = indicators.current_price
        
        # RSI Analysis
        if indicators.rsi_14 is not None:
            total_checks += 1
            if indicators.rsi_14 < 30:
                buy_signals += 1
                reasons.append(f"RSI oversold ({indicators.rsi_14:.1f})")
            elif indicators.rsi_14 > 70:
                sell_signals += 1
                reasons.append(f"RSI overbought ({indicators.rsi_14:.1f})")
        
        # MACD Analysis
        if indicators.macd is not None and indicators.macd_signal is not None:
            total_checks += 1
            if indicators.macd > indicators.macd_signal and indicators.macd_histogram > 0:
                buy_signals += 1
                reasons.append("MACD bullish crossover")
            elif indicators.macd < indicators.macd_signal and indicators.macd_histogram < 0:
                sell_signals += 1
                reasons.append("MACD bearish crossover")
        
        # Moving Average Analysis
        if indicators.sma_20 and indicators.sma_50:
            total_checks += 1
            if current_price > indicators.sma_20 > indicators.sma_50:
                buy_signals += 1
                reasons.append("Price above SMA20 and SMA50")
            elif current_price < indicators.sma_20 < indicators.sma_50:
                sell_signals += 1
                reasons.append("Price below SMA20 and SMA50")
        
        # Golden/Death Cross
        if indicators.sma_50 and indicators.sma_200:
            total_checks += 1
            if indicators.sma_50 > indicators.sma_200:
                buy_signals += 0.5
                reasons.append("Golden cross (SMA50 > SMA200)")
            elif indicators.sma_50 < indicators.sma_200:
                sell_signals += 0.5
                reasons.append("Death cross (SMA50 < SMA200)")
        
        # Bollinger Bands
        if indicators.bb_lower and indicators.bb_upper:
            total_checks += 1
            if current_price < indicators.bb_lower:
                buy_signals += 1
                reasons.append("Price below lower Bollinger Band")
            elif current_price > indicators.bb_upper:
                sell_signals += 1
                reasons.append("Price above upper Bollinger Band")
        
        # Volume confirmation
        if indicators.volume_ratio and indicators.volume_ratio > 2:
            reasons.append(f"Unusual volume ({indicators.volume_ratio:.1f}x)")
        
        # Determine signal
        if total_checks == 0:
            signal = SignalType.NEUTRAL
            confidence = 0.5
        else:
            net_signal = buy_signals - sell_signals
            # Confidence based on signal strength and indicator agreement
            # Max possible net signal is roughly equal to total_checks
            signal_strength = abs(net_signal) / total_checks
            # Boost confidence based on number of agreeing indicators
            agreeing_signals = max(buy_signals, sell_signals)
            agreement_ratio = agreeing_signals / total_checks if total_checks > 0 else 0
            # Combine both factors: strength + agreement
            confidence = min(0.95, 0.4 + (signal_strength * 0.35) + (agreement_ratio * 0.25))
            
            if net_signal >= 2:
                signal = SignalType.STRONG_BUY
                confidence = min(0.95, confidence + 0.1)
            elif net_signal > 0:
                signal = SignalType.BUY
            elif net_signal <= -2:
                signal = SignalType.STRONG_SELL
                confidence = min(0.95, confidence + 0.1)
            elif net_signal < 0:
                signal = SignalType.SELL
            else:
                signal = SignalType.NEUTRAL
                confidence = max(0.5, confidence)  # Neutral should still have decent confidence
        
        return TradingSignal(
            symbol=symbol,
            signal=signal,
            confidence=min(confidence, 1.0),
            reasons=reasons
        )
    
    def analyze_volume(self, symbol: str, df: Optional[pd.DataFrame] = None) -> Optional[VolumeAnalysis]:
        """Analyze volume patterns."""
        if df is None:
            df = self.get_stock_data(symbol)
        
        if df is None or df.empty:
            return None
        
        try:
            volume = df['Volume']
            close = df['Close']
            
            current_volume = int(volume.iloc[-1])
            avg_volume_20d = float(volume.tail(20).mean())
            volume_ratio = current_volume / avg_volume_20d if avg_volume_20d > 0 else 0
            is_unusual = volume_ratio >= 2.0
            
            # Price-Volume correlation
            recent_20d = df.tail(20)
            price_changes = recent_20d['Close'].pct_change()
            volume_changes = recent_20d['Volume'].pct_change()
            correlation = float(price_changes.corr(volume_changes))
            
            return VolumeAnalysis(
                symbol=symbol,
                current_volume=current_volume,
                average_volume_20d=avg_volume_20d,
                volume_ratio=volume_ratio,
                is_unusual=is_unusual,
                price_volume_correlation=correlation if not pd.isna(correlation) else None
            )
        
        except Exception as e:
            print(f"Error analyzing volume for {symbol}: {e}")
            return None
    
    def analyze_volatility(self, symbol: str, df: Optional[pd.DataFrame] = None) -> Optional[VolatilityMetrics]:
        """Analyze volatility metrics."""
        if df is None:
            df = self.get_stock_data(symbol)
        
        if df is None or df.empty:
            return None
        
        try:
            close = df['Close']
            high = df['High']
            low = df['Low']
            
            # Historical volatility (annualized)
            returns_30d = close.tail(30).pct_change().dropna()
            returns_90d = close.tail(90).pct_change().dropna()
            
            hv_30d = float(returns_30d.std() * np.sqrt(252) * 100)
            hv_90d = float(returns_90d.std() * np.sqrt(252) * 100)
            
            # ATR
            atr = AverageTrueRange(high, low, close, window=14).average_true_range()
            atr_14 = float(atr.iloc[-1])
            
            # High volatility threshold
            is_high_volatility = hv_30d > 40.0
            
            return VolatilityMetrics(
                symbol=symbol,
                historical_volatility_30d=hv_30d,
                historical_volatility_90d=hv_90d,
                atr_14=atr_14,
                is_high_volatility=is_high_volatility
            )
        
        except Exception as e:
            print(f"Error analyzing volatility for {symbol}: {e}")
            return None
    
    def detect_patterns(self, symbol: str, df: Optional[pd.DataFrame] = None) -> list[PatternRecognition]:
        """Detect chart patterns (basic implementation)."""
        if df is None:
            df = self.get_stock_data(symbol)
        
        if df is None or df.empty:
            return []
        
        patterns = []
        
        try:
            close = df['Close']
            recent_50 = close.tail(50)
            
            # Breakout detection
            recent_high = recent_50.max()
            current_price = close.iloc[-1]
            
            if current_price >= recent_high * 0.99:  # Within 1% of high
                patterns.append(PatternRecognition(
                    symbol=symbol,
                    pattern=PricePattern.BREAKOUT_UP,
                    confidence=0.7,
                    description="Price breaking out to new 50-day high"
                ))
            
            # Consolidation (low volatility)
            volatility = recent_50.pct_change().std()
            if volatility < 0.01:  # Less than 1% daily volatility
                patterns.append(PatternRecognition(
                    symbol=symbol,
                    pattern=PricePattern.CONSOLIDATION,
                    confidence=0.6,
                    description="Price consolidating with low volatility"
                ))
        
        except Exception as e:
            print(f"Error detecting patterns for {symbol}: {e}")
        
        return patterns
