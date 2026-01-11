"""Data models for sentiment service."""
from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class SentimentSource(str, Enum):
    """Source of sentiment data."""
    NEWS = "news"
    REDDIT = "reddit"
    TWITTER = "twitter"
    COMBINED = "combined"


class SentimentScore(str, Enum):
    """Sentiment classification."""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


# Alias for analyzer compatibility
class SentimentLabel(str, Enum):
    """Sentiment label for analyzer."""
    VERY_BEARISH = "very_bearish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    BULLISH = "bullish"
    VERY_BULLISH = "very_bullish"


class SentimentTrend(str, Enum):
    """Sentiment trend direction."""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"


class NewsSource(str, Enum):
    """News source type."""
    YFINANCE = "yfinance"
    GOOGLE_NEWS = "google_news"
    ECONOMIC_TIMES = "economic_times"
    MONEYCONTROL = "moneycontrol"


class SentimentAnalysis(BaseModel):
    """Sentiment analysis result."""
    symbol: str
    score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score from -1 to 1")
    classification: SentimentScore
    source: SentimentSource
    confidence: float = Field(..., ge=0.0, le=1.0)
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    sample_size: int = Field(..., ge=0, description="Number of items analyzed")


class NewsArticle(BaseModel):
    """News article for sentiment analysis."""
    title: str
    source: str = "unknown"
    url: Optional[str] = None
    published_at: Optional[datetime] = None
    summary: Optional[str] = None
    # Optional fields for existing compatibility
    description: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_classification: Optional[SentimentScore] = None


class ArticleSentiment(BaseModel):
    """Analyzed article with sentiment scores."""
    article: NewsArticle
    sentiment: SentimentLabel
    confidence: float
    positive_score: float
    negative_score: float
    neutral_score: float
    key_phrases: List[str] = Field(default_factory=list)
    model_version: str = "rule_based_v1"


class SocialPost(BaseModel):
    """Social media post with sentiment."""
    platform: str  # reddit, twitter
    content: str
    author: str
    url: Optional[str] = None
    created_at: datetime
    upvotes: int = 0
    comments: int = 0
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    sentiment_classification: SentimentScore


class StockSentiment(BaseModel):
    """Comprehensive sentiment for a stock."""
    symbol: str
    company_name: Optional[str] = None
    overall_sentiment: SentimentLabel = SentimentLabel.NEUTRAL
    overall_score: float = Field(0.0, ge=-1.0, le=1.0)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    news_sentiment_score: float = 0.0
    articles_analyzed: int = 0
    positive_articles: int = 0
    negative_articles: int = 0
    neutral_articles: int = 0
    top_positive_articles: List[ArticleSentiment] = Field(default_factory=list)
    top_negative_articles: List[ArticleSentiment] = Field(default_factory=list)
    sentiment_trend: Optional[SentimentTrend] = None
    # For API compatibility
    overall_classification: Optional[SentimentScore] = None
    news_sentiment: Optional[SentimentAnalysis] = None
    reddit_sentiment: Optional[SentimentAnalysis] = None
    twitter_sentiment: Optional[SentimentAnalysis] = None
    trending_score: float = Field(0.0, ge=0.0, description="How trending the stock is")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    recent_news: List[NewsArticle] = Field(default_factory=list)
    recent_posts: List[SocialPost] = Field(default_factory=list)


class TrendingStock(BaseModel):
    """Trending stock based on sentiment and mentions."""
    symbol: str
    company_name: Optional[str] = None
    mention_count: int
    sentiment_score: float
    sentiment_classification: SentimentScore
    trending_score: float
    price_change_percent: Optional[float] = None
