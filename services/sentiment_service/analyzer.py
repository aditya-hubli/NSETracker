"""
Sentiment Analysis Engine

This module provides sentiment analysis for stock-related news and text.

Implementation: FinBERT ML model (ProsusAI/finbert)
Fallback: Rule-based keyword analysis

FinBERT is a pre-trained NLP model to analyze sentiment of financial text.
"""

import os
import re
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
from collections import Counter

from .models import (
    SentimentLabel, NewsArticle, ArticleSentiment, 
    StockSentiment, SentimentTrend
)

# ML Model Configuration
ML_ENABLED = os.getenv("ENABLE_ML_SENTIMENT", "true").lower() == "true"
ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", "./models/finbert")

# Global model instance (loaded once)
_finbert_model = None
_finbert_tokenizer = None


def _load_finbert():
    """Load FinBERT model (singleton pattern)."""
    global _finbert_model, _finbert_tokenizer
    
    if _finbert_model is not None:
        return True
    
    try:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        
        model_path = ML_MODEL_PATH
        if not os.path.exists(model_path):
            # Try relative to project root
            model_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "models", "finbert"
            )
        
        if os.path.exists(model_path):
            print(f"Loading FinBERT from {model_path}...")
            _finbert_tokenizer = AutoTokenizer.from_pretrained(model_path)
            _finbert_model = AutoModelForSequenceClassification.from_pretrained(model_path)
            _finbert_model.eval()  # Set to evaluation mode
            print("FinBERT loaded successfully!")
            return True
        else:
            print(f"FinBERT model not found at {model_path}, using rule-based fallback")
            return False
    except Exception as e:
        print(f"Failed to load FinBERT: {e}, using rule-based fallback")
        return False


class SentimentAnalyzer:
    """
    Sentiment Analysis Engine using FinBERT.
    
    FinBERT is a BERT model fine-tuned on financial text.
    Falls back to rule-based analysis if model unavailable.
    """
    
    def __init__(self, use_ml: bool = True):
        """
        Initialize analyzer.
        
        Args:
            use_ml: Whether to use ML model (default: True)
        """
        self._use_ml = use_ml and ML_ENABLED
        self._model_loaded = False
        
        if self._use_ml:
            self._model_loaded = _load_finbert()
        
        # Rule-based sentiment keywords (Indian market context)
        self._positive_keywords = {
            # Strong positive
            'surge', 'soar', 'rally', 'boom', 'breakthrough', 'record high',
            'outperform', 'beat estimates', 'strong growth', 'bullish',
            'upgrade', 'buy rating', 'target raised', 'expansion',
            
            # Moderate positive
            'gain', 'rise', 'profit', 'growth', 'increase', 'improve',
            'positive', 'optimistic', 'recovery', 'upside', 'momentum',
            'dividend', 'acquisition', 'partnership', 'contract win',
            
            # Indian market specific
            'nifty high', 'sensex gains', 'fii buying', 'dii support',
            'quarterly results beat', 'order book strong', 'capacity expansion'
        }
        
        self._negative_keywords = {
            # Strong negative
            'crash', 'plunge', 'collapse', 'crisis', 'scandal', 'fraud',
            'downgrade', 'sell rating', 'target cut', 'bankruptcy',
            'default', 'investigation', 'regulatory action',
            
            # Moderate negative
            'fall', 'drop', 'decline', 'loss', 'miss', 'weak',
            'concern', 'risk', 'warning', 'slowdown', 'pressure',
            'debt', 'layoff', 'restructuring', 'impairment',
            
            # Indian market specific
            'nifty falls', 'sensex drops', 'fii selling', 'rbi warning',
            'sebi action', 'promoter selling', 'margin pressure'
        }
        
        self._intensifiers = {
            'very', 'extremely', 'significantly', 'sharply', 'strongly',
            'massive', 'huge', 'major', 'substantial'
        }
        
        self._negators = {
            'not', 'no', 'never', 'neither', 'hardly', 'barely',
            'despite', 'although', 'however'
        }
    
    def analyze_article(self, article: NewsArticle) -> ArticleSentiment:
        """
        Analyze sentiment of a single news article.
        
        Args:
            article: NewsArticle object
            
        Returns:
            ArticleSentiment with scores and classification
        """
        # Combine title and summary for analysis
        text = article.title
        if article.summary:
            text += " " + article.summary
        
        # Get sentiment scores
        scores = self._analyze_text(text)
        
        # Determine overall sentiment
        sentiment, confidence = self._classify_sentiment(scores)
        
        # Extract key phrases
        key_phrases = self._extract_key_phrases(text)
        
        return ArticleSentiment(
            article=article,
            sentiment=sentiment,
            confidence=confidence,
            positive_score=scores['positive'],
            negative_score=scores['negative'],
            neutral_score=scores['neutral'],
            key_phrases=key_phrases,
            model_version="finbert_v1" if self._model_loaded else "rule_based_v1"
        )
    
    def analyze_stock(
        self,
        symbol: str,
        company_name: str,
        articles: List[NewsArticle]
    ) -> StockSentiment:
        """
        Analyze overall sentiment for a stock based on multiple articles.
        
        Args:
            symbol: Stock symbol
            company_name: Company name
            articles: List of news articles
            
        Returns:
            StockSentiment with aggregated analysis
        """
        if not articles:
            return StockSentiment(
                symbol=symbol,
                company_name=company_name,
                overall_sentiment=SentimentLabel.NEUTRAL,
                overall_score=0.0,
                confidence=0.0,
                news_sentiment_score=0.0,
                articles_analyzed=0,
                positive_articles=0,
                negative_articles=0,
                neutral_articles=0
            )
        
        # Analyze each article
        analyzed = [self.analyze_article(article) for article in articles]
        
        # Count sentiments
        sentiment_counts = Counter(a.sentiment for a in analyzed)
        positive_count = sentiment_counts.get(SentimentLabel.BULLISH, 0) + \
                        sentiment_counts.get(SentimentLabel.VERY_BULLISH, 0)
        negative_count = sentiment_counts.get(SentimentLabel.BEARISH, 0) + \
                        sentiment_counts.get(SentimentLabel.VERY_BEARISH, 0)
        neutral_count = sentiment_counts.get(SentimentLabel.NEUTRAL, 0)
        
        # Calculate aggregate score (-1 to 1)
        total = len(analyzed)
        weighted_scores = []
        for a in analyzed:
            weight = a.confidence
            if a.sentiment in [SentimentLabel.VERY_BULLISH, SentimentLabel.BULLISH]:
                weighted_scores.append(a.positive_score * weight)
            elif a.sentiment in [SentimentLabel.VERY_BEARISH, SentimentLabel.BEARISH]:
                weighted_scores.append(-a.negative_score * weight)
            else:
                weighted_scores.append(0)
        
        overall_score = sum(weighted_scores) / total if total > 0 else 0
        
        # Determine overall sentiment
        overall_sentiment = self._score_to_sentiment(overall_score)
        
        # Calculate confidence
        confidence = sum(a.confidence for a in analyzed) / total if total > 0 else 0
        
        # Get top articles
        sorted_by_positive = sorted(analyzed, key=lambda x: x.positive_score, reverse=True)
        sorted_by_negative = sorted(analyzed, key=lambda x: x.negative_score, reverse=True)
        
        return StockSentiment(
            symbol=symbol,
            company_name=company_name,
            overall_sentiment=overall_sentiment,
            overall_score=round(overall_score, 3),
            confidence=round(confidence, 3),
            news_sentiment_score=round(overall_score, 3),
            articles_analyzed=total,
            positive_articles=positive_count,
            negative_articles=negative_count,
            neutral_articles=neutral_count,
            top_positive_articles=sorted_by_positive[:3],
            top_negative_articles=sorted_by_negative[:3],
            sentiment_trend=self._calculate_trend(analyzed)
        )
    
    def _analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze text and return sentiment scores.
        
        Uses FinBERT if loaded, otherwise falls back to rule-based.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with 'positive', 'negative', 'neutral' scores
        """
        if self._model_loaded:
            return self._ml_analyze(text)
        
        return self._rule_based_analyze(text)
    
    def _rule_based_analyze(self, text: str) -> Dict[str, float]:
        """
        Rule-based keyword analysis (fallback).
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with 'positive', 'negative', 'neutral' scores
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        positive_matches = 0
        negative_matches = 0
        
        # Count keyword matches
        for keyword in self._positive_keywords:
            if keyword in text_lower:
                positive_matches += 1
                # Check for intensifiers
                for intensifier in self._intensifiers:
                    if f"{intensifier} {keyword}" in text_lower:
                        positive_matches += 0.5
        
        for keyword in self._negative_keywords:
            if keyword in text_lower:
                negative_matches += 1
                for intensifier in self._intensifiers:
                    if f"{intensifier} {keyword}" in text_lower:
                        negative_matches += 0.5
        
        # Check for negations (simple approach)
        for negator in self._negators:
            if negator in words:
                # Swap scores if negation found near sentiment words
                positive_matches, negative_matches = negative_matches * 0.5, positive_matches * 0.5
                break
        
        # Normalize scores
        total = positive_matches + negative_matches + 1  # +1 to avoid division by zero
        
        positive_score = min(1.0, positive_matches / (total * 0.5))
        negative_score = min(1.0, negative_matches / (total * 0.5))
        neutral_score = max(0.0, 1.0 - positive_score - negative_score)
        
        return {
            'positive': round(positive_score, 3),
            'negative': round(negative_score, 3),
            'neutral': round(neutral_score, 3)
        }
    
    def _ml_analyze(self, text: str) -> Dict[str, float]:
        """
        Analyze text using FinBERT model.
        
        FinBERT output labels (from config):
        - 0: positive
        - 1: negative  
        - 2: neutral
        """
        import torch
        
        global _finbert_model, _finbert_tokenizer
        
        try:
            # Tokenize input
            inputs = _finbert_tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512,
                padding=True
            )
            
            # Run inference
            with torch.no_grad():
                outputs = _finbert_model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)[0]
            
            # FinBERT: [positive, negative, neutral]
            return {
                'positive': float(probs[0]),
                'negative': float(probs[1]),
                'neutral': float(probs[2])
            }
        except Exception as e:
            print(f"FinBERT inference error: {e}")
            # Fallback to rule-based
            return self._rule_based_analyze(text)
        # Placeholder - returns neutral
        return {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
    
    def _classify_sentiment(self, scores: Dict[str, float]) -> Tuple[SentimentLabel, float]:
        """Classify sentiment based on scores"""
        pos = scores['positive']
        neg = scores['negative']
        
        # Calculate confidence
        confidence = max(pos, neg, scores['neutral'])
        
        # Determine sentiment
        if pos > 0.7:
            return SentimentLabel.VERY_BULLISH, confidence
        elif pos > 0.5:
            return SentimentLabel.BULLISH, confidence
        elif neg > 0.7:
            return SentimentLabel.VERY_BEARISH, confidence
        elif neg > 0.5:
            return SentimentLabel.BEARISH, confidence
        else:
            return SentimentLabel.NEUTRAL, confidence
    
    def _score_to_sentiment(self, score: float) -> SentimentLabel:
        """Convert aggregate score to sentiment label"""
        if score > 0.5:
            return SentimentLabel.VERY_BULLISH
        elif score > 0.2:
            return SentimentLabel.BULLISH
        elif score < -0.5:
            return SentimentLabel.VERY_BEARISH
        elif score < -0.2:
            return SentimentLabel.BEARISH
        else:
            return SentimentLabel.NEUTRAL
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key sentiment-bearing phrases"""
        text_lower = text.lower()
        phrases = []
        
        # Find matching keywords in context
        for keyword in self._positive_keywords | self._negative_keywords:
            if keyword in text_lower:
                # Get surrounding context
                idx = text_lower.find(keyword)
                start = max(0, idx - 20)
                end = min(len(text), idx + len(keyword) + 20)
                context = text[start:end].strip()
                if context and len(context) > 5:
                    phrases.append(context)
        
        return phrases[:5]  # Limit to 5 key phrases
    
    def _calculate_trend(self, analyzed: List[ArticleSentiment]) -> str:
        """Calculate sentiment trend from articles"""
        if len(analyzed) < 2:
            return "stable"
        
        # Simple trend: compare first half vs second half
        mid = len(analyzed) // 2
        first_half_score = sum(
            a.positive_score - a.negative_score for a in analyzed[:mid]
        ) / mid
        second_half_score = sum(
            a.positive_score - a.negative_score for a in analyzed[mid:]
        ) / (len(analyzed) - mid)
        
        diff = second_half_score - first_half_score
        
        if diff > 0.1:
            return "improving"
        elif diff < -0.1:
            return "declining"
        else:
            return "stable"


# Future ML Model Classes (placeholders)

class FinBERTModel:
    """
    Future: FinBERT for financial sentiment analysis
    
    - Pre-trained on financial news and reports
    - Fine-tuned on Indian market data
    - Supports Hindi-English code-mixed text
    """
    pass


class CustomLSTMModel:
    """
    Future: Custom LSTM for Indian market sentiment
    
    - Trained on NSE/BSE news corpus
    - Handles Indian financial terminology
    - Real-time inference capability
    """
    pass


class LLMSentimentModel:
    """
    Future: LLM-based sentiment analysis
    
    - Uses GPT/Claude/Llama for nuanced analysis
    - Provides explanations for sentiment
    - Can analyze complex market narratives
    """
    pass
