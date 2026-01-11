"""API routes for sentiment service."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from .models import StockSentiment, SentimentScore, SentimentLabel, NewsArticle
from .analyzer import SentimentAnalyzer
from .news_fetcher import NewsFetcher

router = APIRouter(prefix="/sentiment", tags=["sentiment"])

# Initialize analyzer and news fetcher (singletons)
_analyzer: Optional[SentimentAnalyzer] = None
_news_fetcher: Optional[NewsFetcher] = None


def get_analyzer() -> SentimentAnalyzer:
    """Get or create sentiment analyzer (singleton)."""
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    return _analyzer


def get_news_fetcher() -> NewsFetcher:
    """Get or create news fetcher (singleton)."""
    global _news_fetcher
    if _news_fetcher is None:
        _news_fetcher = NewsFetcher()
    return _news_fetcher


@router.get("/stock/{symbol}")
async def get_stock_sentiment(
    symbol: str,
    refresh: bool = Query(False, description="Force refresh sentiment data"),
):
    """
    Get comprehensive sentiment analysis for a stock using FinBERT.
    
    Returns ML-powered sentiment analysis from news articles.
    """
    symbol = symbol.upper()
    
    # Fetch news articles
    news_fetcher = get_news_fetcher()
    articles = await news_fetcher.fetch_news(symbol, max_articles=10, days_back=7)
    
    if not articles:
        # Return neutral sentiment if no news
        return {
            "symbol": symbol,
            "overall_score": 0.0,
            "overall_classification": "neutral",
            "confidence": 0.0,
            "articles_analyzed": 0,
            "positive_articles": 0,
            "negative_articles": 0,
            "neutral_articles": 0,
            "trending_score": 0.0,
            "model_version": "finbert_v1" if get_analyzer()._model_loaded else "rule_based_v1",
            "recent_news": [],
            "last_updated": datetime.utcnow().isoformat()
        }
    
    # Analyze with FinBERT
    analyzer = get_analyzer()
    
    # Get company name from symbol
    company_name = symbol.replace('.NS', '').replace('.BO', '')
    
    # Analyze each article
    analyzed_articles = []
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    total_score = 0.0
    total_confidence = 0.0
    
    for article in articles:
        result = analyzer.analyze_article(article)
        analyzed_articles.append({
            "title": article.title,
            "source": article.source,
            "url": article.url,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "sentiment": result.sentiment.value,
            "confidence": round(result.confidence, 3),
            "positive_score": round(result.positive_score, 3),
            "negative_score": round(result.negative_score, 3),
        })
        
        # Count sentiments
        if result.sentiment in [SentimentLabel.BULLISH, SentimentLabel.VERY_BULLISH]:
            positive_count += 1
            total_score += result.positive_score
        elif result.sentiment in [SentimentLabel.BEARISH, SentimentLabel.VERY_BEARISH]:
            negative_count += 1
            total_score -= result.negative_score
        else:
            neutral_count += 1
        
        total_confidence += result.confidence
    
    # Calculate overall metrics
    num_articles = len(articles)
    avg_score = total_score / num_articles if num_articles > 0 else 0
    avg_confidence = total_confidence / num_articles if num_articles > 0 else 0
    
    # Classify overall sentiment
    if avg_score > 0.3:
        overall_class = "positive" if avg_score < 0.6 else "very_positive"
    elif avg_score < -0.3:
        overall_class = "negative" if avg_score > -0.6 else "very_negative"
    else:
        overall_class = "neutral"
    
    return {
        "symbol": symbol,
        "company_name": company_name,
        "overall_score": round(avg_score, 3),
        "overall_classification": overall_class,
        "confidence": round(avg_confidence, 3),
        "articles_analyzed": num_articles,
        "positive_articles": positive_count,
        "negative_articles": negative_count,
        "neutral_articles": neutral_count,
        "trending_score": num_articles * (1 + avg_score),
        "model_version": "finbert_v1" if analyzer._model_loaded else "rule_based_v1",
        "recent_news": analyzed_articles,
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/analyze")
async def analyze_text(
    text: str = Query(..., description="Text to analyze"),
):
    """
    Analyze sentiment of any financial text using FinBERT.
    
    Useful for testing or analyzing custom text.
    """
    analyzer = get_analyzer()
    scores = analyzer._analyze_text(text)
    
    # Determine sentiment
    if scores['positive'] > scores['negative'] and scores['positive'] > scores['neutral']:
        sentiment = "positive"
        confidence = scores['positive']
    elif scores['negative'] > scores['positive'] and scores['negative'] > scores['neutral']:
        sentiment = "negative"
        confidence = scores['negative']
    else:
        sentiment = "neutral"
        confidence = scores['neutral']
    
    return {
        "text": text[:200] + "..." if len(text) > 200 else text,
        "sentiment": sentiment,
        "confidence": round(confidence, 3),
        "scores": {
            "positive": round(scores['positive'], 3),
            "negative": round(scores['negative'], 3),
            "neutral": round(scores['neutral'], 3),
        },
        "model": "finbert" if analyzer._model_loaded else "rule_based"
    }


@router.get("/health")
async def health_check():
    """Check sentiment service health and model status."""
    analyzer = get_analyzer()
    return {
        "status": "healthy",
        "model_loaded": analyzer._model_loaded,
        "model_version": "finbert_v1" if analyzer._model_loaded else "rule_based_v1"
    }


@router.get("/{symbol}/news")
async def get_stock_news(symbol: str):
    """
    Get news articles with sentiment analysis for a stock.
    
    This endpoint is used by the News page in the dashboard.
    """
    symbol = symbol.upper()
    
    # Fetch news articles
    news_fetcher = get_news_fetcher()
    articles = await news_fetcher.fetch_news(symbol, max_articles=15, days_back=7)
    
    if not articles:
        return {
            "symbol": symbol,
            "news": [],
            "overall_sentiment": "neutral",
            "sentiment_score": 0.0,
        }
    
    # Analyze with sentiment
    analyzer = get_analyzer()
    
    news_items = []
    total_score = 0.0
    
    for article in articles:
        result = analyzer.analyze_article(article)
        
        # Map sentiment labels to simpler format
        sentiment_label = result.sentiment.value
        if sentiment_label in ['bullish', 'very_bullish']:
            simple_label = 'positive'
        elif sentiment_label in ['bearish', 'very_bearish']:
            simple_label = 'negative'
        else:
            simple_label = 'neutral'
        
        # Calculate score contribution
        if simple_label == 'positive':
            total_score += result.confidence
        elif simple_label == 'negative':
            total_score -= result.confidence
        
        news_items.append({
            "title": article.title,
            "description": article.summary,
            "url": article.url,
            "source": article.source,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "sentiment": {
                "label": simple_label,
                "score": round(result.confidence, 2),
            }
        })
    
    # Calculate overall sentiment
    avg_score = total_score / len(articles) if articles else 0
    if avg_score > 0.2:
        overall = "positive"
    elif avg_score < -0.2:
        overall = "negative"
    else:
        overall = "neutral"
    
    return {
        "symbol": symbol,
        "news": news_items,
        "overall_sentiment": overall,
        "sentiment_score": round(avg_score, 2),
    }

