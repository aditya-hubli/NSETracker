"""
Technical Analysis Engine

This module contains the core analysis logic. Currently uses rule-based
technical indicators. Designed to be extended with ML models later.

Future ML Integration Points:
1. Replace rule-based recommendation with ML prediction
2. Add pattern recognition using CNN/LSTM models
3. Add price prediction using time series models
4. Add anomaly detection for unusual trading patterns
"""

import numpy as np
from typing import List, Optional, Tuple
from datetime import datetime
from .models import (
    PriceData, TechnicalIndicators, AnalysisResult
)


class TechnicalAnalyzer:
    """
    Technical Analysis Engine
    
    Currently implements rule-based analysis.
    Ready for ML model integration via the predict() method.
    """
    
    def __init__(self, ml_model=None):
        """
        Initialize analyzer with optional ML model.
        
        Args:
            ml_model: Future ML model instance (e.g., TensorFlow, PyTorch model)
        """
        self.ml_model = ml_model
        self._model_loaded = ml_model is not None
    
    def analyze(
        self,
        symbol: str,
        name: str,
        price_data: List[PriceData],
        current_price: float,
        price_change: float,
        price_change_percent: float
    ) -> AnalysisResult:
        """
        Perform complete technical analysis on a stock.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE.NS")
            name: Company name
            price_data: Historical price data
            current_price: Current stock price
            price_change: Price change from previous close
            price_change_percent: Percentage change
            
        Returns:
            AnalysisResult with indicators and recommendation
        """
        if len(price_data) < 20:
            raise ValueError(f"Insufficient data points: {len(price_data)}. Need at least 20.")
        
        # Extract price arrays
        closes = np.array([p.close for p in price_data])
        highs = np.array([p.high for p in price_data])
        lows = np.array([p.low for p in price_data])
        
        # Calculate technical indicators
        indicators = self._calculate_indicators(closes, highs, lows, current_price)
        
        # Calculate recommendation score
        score = self._calculate_score(indicators, current_price)
        recommendation = self._score_to_recommendation(score)
        confidence = self._calculate_confidence(score, indicators)
        
        # Future: Use ML model if available
        ml_prediction = None
        if self._model_loaded:
            ml_prediction = self._ml_predict(price_data)
        
        return AnalysisResult(
            symbol=symbol,
            name=name,
            current_price=current_price,
            price_change=price_change,
            price_change_percent=price_change_percent,
            indicators=indicators,
            recommendation=recommendation,
            confidence=confidence,
            score=score,
            analyzed_at=datetime.utcnow(),
            data_points=len(price_data),
            ml_prediction=ml_prediction
        )
    
    def _calculate_indicators(
        self,
        closes: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        current_price: float
    ) -> TechnicalIndicators:
        """Calculate all technical indicators"""
        
        # RSI (14-period)
        rsi = self._calculate_rsi(closes, period=14)
        rsi_signal = "oversold" if rsi < 30 else "overbought" if rsi > 70 else "neutral"
        
        # Simple Moving Averages
        sma_20 = self._calculate_sma(closes, period=20)
        sma_50 = self._calculate_sma(closes, period=min(50, len(closes)))
        
        # Exponential Moving Averages (for MACD)
        ema_12 = self._calculate_ema(closes, period=12)
        ema_26 = self._calculate_ema(closes, period=26)
        
        # MACD
        macd = ema_12 - ema_26
        macd_signal = self._calculate_ema(np.array([macd]), period=9) if len(closes) > 26 else None
        macd_histogram = macd - macd_signal if macd_signal else None
        
        # Bollinger Bands
        bb_middle = sma_20
        std_20 = np.std(closes[-20:])
        bb_upper = bb_middle + (2 * std_20)
        bb_lower = bb_middle - (2 * std_20)
        
        # Support & Resistance (30-day)
        support = float(np.min(lows[-30:]))
        resistance = float(np.max(highs[-30:]))
        
        # Trend
        if current_price > sma_20 and sma_20 > sma_50:
            trend = "bullish"
        elif current_price < sma_20 and sma_20 < sma_50:
            trend = "bearish"
        else:
            trend = "neutral"
        
        # Momentum
        price_vs_sma = abs(current_price - sma_20) / sma_20
        if price_vs_sma > 0.03:
            momentum = "strong"
        elif price_vs_sma < 0.01:
            momentum = "weak"
        else:
            momentum = "neutral"
        
        # Volatility
        volatility_pct = (std_20 / sma_20) * 100
        if volatility_pct > 3:
            volatility = "high"
        elif volatility_pct < 1.5:
            volatility = "low"
        else:
            volatility = "medium"
        
        return TechnicalIndicators(
            rsi=round(rsi, 2),
            rsi_signal=rsi_signal,
            sma_20=round(sma_20, 2),
            sma_50=round(sma_50, 2),
            ema_12=round(ema_12, 2),
            ema_26=round(ema_26, 2),
            macd=round(macd, 2) if macd else None,
            macd_signal=round(macd_signal, 2) if macd_signal else None,
            macd_histogram=round(macd_histogram, 2) if macd_histogram else None,
            bb_upper=round(bb_upper, 2),
            bb_middle=round(bb_middle, 2),
            bb_lower=round(bb_lower, 2),
            trend=trend,
            momentum=momentum,
            volatility=volatility,
            support=round(support, 2),
            resistance=round(resistance, 2)
        )
    
    def _calculate_rsi(self, closes: np.ndarray, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)
    
    def _calculate_sma(self, data: np.ndarray, period: int) -> float:
        """Calculate Simple Moving Average"""
        return float(np.mean(data[-period:]))
    
    def _calculate_ema(self, data: np.ndarray, period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(data) < period:
            return float(np.mean(data))
        
        multiplier = 2 / (period + 1)
        ema = data[-period]
        
        for price in data[-period + 1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return float(ema)
    
    def _calculate_score(self, indicators: TechnicalIndicators, current_price: float) -> float:
        """
        Calculate recommendation score (0-100).
        
        This is the rule-based scoring system.
        Future: Replace with ML model prediction.
        """
        score = 50.0  # Start neutral
        
        # RSI contribution (-20 to +20)
        if indicators.rsi < 30:
            score += 20
        elif indicators.rsi < 40:
            score += 10
        elif indicators.rsi > 70:
            score -= 20
        elif indicators.rsi > 60:
            score -= 10
        
        # Trend contribution (-15 to +15)
        if indicators.trend == "bullish":
            score += 15
        elif indicators.trend == "bearish":
            score -= 15
        
        # Price vs SMA contribution (-10 to +10)
        if current_price > indicators.sma_20:
            score += 10
        else:
            score -= 10
        
        # Support/Resistance position (-10 to +10)
        price_range = indicators.resistance - indicators.support
        if price_range > 0:
            position = (current_price - indicators.support) / price_range
            if position < 0.2:  # Near support
                score += 10
            elif position > 0.8:  # Near resistance
                score -= 10
        
        # MACD contribution (-5 to +5)
        if indicators.macd is not None and indicators.macd_signal is not None:
            if indicators.macd > indicators.macd_signal:
                score += 5
            else:
                score -= 5
        
        # Bollinger Bands contribution (-5 to +5)
        if indicators.bb_lower and indicators.bb_upper:
            if current_price < indicators.bb_lower:
                score += 5  # Oversold
            elif current_price > indicators.bb_upper:
                score -= 5  # Overbought
        
        return max(0, min(100, score))
    
    def _score_to_recommendation(self, score: float) -> str:
        """Convert score to recommendation label"""
        if score >= 75:
            return "Strong Buy"
        elif score >= 60:
            return "Buy"
        elif score >= 40:
            return "Hold"
        elif score >= 25:
            return "Sell"
        else:
            return "Strong Sell"
    
    def _calculate_confidence(self, score: float, indicators: TechnicalIndicators) -> float:
        """
        Calculate confidence level for the recommendation.
        
        Future: Use ML model's prediction probability.
        """
        # Base confidence from score distance from neutral
        base_confidence = 50 + abs(score - 50)
        
        # Adjust based on indicator alignment
        alignment_bonus = 0
        
        # RSI and trend alignment
        if (indicators.rsi_signal == "oversold" and indicators.trend == "bullish") or \
           (indicators.rsi_signal == "overbought" and indicators.trend == "bearish"):
            alignment_bonus += 10
        
        # Momentum alignment
        if indicators.momentum == "strong":
            alignment_bonus += 5
        
        confidence = min(95, max(40, base_confidence + alignment_bonus))
        return round(confidence, 1)
    
    def _ml_predict(self, price_data: List[PriceData]) -> Optional[dict]:
        """
        Make prediction using ML model.
        
        This is a placeholder for future ML integration.
        When implementing, this method will:
        1. Preprocess price data for the model
        2. Run inference
        3. Return prediction with confidence
        
        Example future implementation:
        ```python
        features = self._prepare_features(price_data)
        prediction = self.ml_model.predict(features)
        return {
            "predicted_direction": "up" if prediction > 0.5 else "down",
            "probability": float(prediction),
            "model_version": self.ml_model.version
        }
        ```
        """
        if not self._model_loaded:
            return None
        
        # Placeholder for ML prediction
        return {
            "model_status": "not_implemented",
            "message": "ML model integration pending"
        }


# Future ML Model Classes (placeholders)

class PricePredictionModel:
    """
    Future: LSTM/Transformer model for price prediction
    
    Example implementation:
    - Input: Last N days of OHLCV data
    - Output: Predicted price for next 1/5/10 days
    - Architecture: LSTM or Transformer-based
    """
    pass


class PatternRecognitionModel:
    """
    Future: CNN model for chart pattern recognition
    
    Example implementation:
    - Input: Price chart as image or time series
    - Output: Detected patterns (head & shoulders, double top, etc.)
    - Architecture: CNN or Vision Transformer
    """
    pass


class AnomalyDetectionModel:
    """
    Future: Autoencoder for detecting unusual trading patterns
    
    Example implementation:
    - Input: Volume, price, and volatility features
    - Output: Anomaly score
    - Architecture: Variational Autoencoder
    """
    pass
