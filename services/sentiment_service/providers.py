"""Sentiment data providers - News, Reddit, Twitter."""
import asyncio
from datetime import datetime, timedelta
from typing import Optional

import httpx
import praw
from newsapi import NewsApiClient
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from shared.config import get_settings
from .models import (
    NewsArticle,
    SentimentAnalysis,
    SentimentScore,
    SentimentSource,
    SocialPost,
)


class SentimentAnalyzer:
    """Analyze sentiment from text using multiple methods."""
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
    
    def analyze(self, text: str) -> tuple[float, SentimentScore]:
        """
        Analyze sentiment and return score and classification.
        
        Returns:
            Tuple of (score: -1 to 1, classification)
        """
        # Use VADER for social media text (better for informal text)
        vader_scores = self.vader.polarity_scores(text)
        compound_score = vader_scores['compound']
        
        # Classify based on compound score
        if compound_score <= -0.6:
            classification = SentimentScore.VERY_NEGATIVE
        elif compound_score <= -0.2:
            classification = SentimentScore.NEGATIVE
        elif compound_score < 0.2:
            classification = SentimentScore.NEUTRAL
        elif compound_score < 0.6:
            classification = SentimentScore.POSITIVE
        else:
            classification = SentimentScore.VERY_POSITIVE
        
        return compound_score, classification


class NewsProvider:
    """Fetch and analyze news sentiment."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_settings().news_api_key
        self.client = NewsApiClient(api_key=self.api_key) if self.api_key else None
        self.analyzer = SentimentAnalyzer()
    
    async def get_stock_news(
        self, 
        symbol: str, 
        days: int = 7,
        max_articles: int = 20
    ) -> list[NewsArticle]:
        """Fetch recent news for a stock."""
        if not self.client:
            return []
        
        try:
            # Calculate date range
            to_date = datetime.utcnow()
            from_date = to_date - timedelta(days=days)
            
            # Fetch news
            articles = await asyncio.to_thread(
                self.client.get_everything,
                q=f"{symbol} stock OR company",
                from_param=from_date.isoformat(),
                to=to_date.isoformat(),
                language='en',
                sort_by='publishedAt',
                page_size=max_articles
            )
            
            news_articles = []
            for article in articles.get('articles', []):
                # Analyze sentiment
                text = f"{article.get('title', '')} {article.get('description', '')}"
                score, classification = self.analyzer.analyze(text)
                
                news_articles.append(NewsArticle(
                    title=article['title'],
                    description=article.get('description'),
                    url=article['url'],
                    source=article['source']['name'],
                    published_at=datetime.fromisoformat(
                        article['publishedAt'].replace('Z', '+00:00')
                    ),
                    sentiment_score=score,
                    sentiment_classification=classification
                ))
            
            return news_articles
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    async def get_sentiment_analysis(self, symbol: str) -> Optional[SentimentAnalysis]:
        """Get overall news sentiment for a stock."""
        articles = await self.get_stock_news(symbol)
        
        if not articles:
            return None
        
        # Calculate average sentiment
        avg_score = sum(a.sentiment_score for a in articles) / len(articles)
        
        # Determine classification
        analyzer = SentimentAnalyzer()
        _, classification = analyzer.analyze("")  # Use score to classify
        if avg_score <= -0.6:
            classification = SentimentScore.VERY_NEGATIVE
        elif avg_score <= -0.2:
            classification = SentimentScore.NEGATIVE
        elif avg_score < 0.2:
            classification = SentimentScore.NEUTRAL
        elif avg_score < 0.6:
            classification = SentimentScore.POSITIVE
        else:
            classification = SentimentScore.VERY_POSITIVE
        
        return SentimentAnalysis(
            symbol=symbol,
            score=avg_score,
            classification=classification,
            source=SentimentSource.NEWS,
            confidence=min(len(articles) / 20.0, 1.0),  # More articles = higher confidence
            sample_size=len(articles)
        )


class RedditProvider:
    """Fetch and analyze Reddit sentiment."""
    
    def __init__(
        self, 
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        settings = get_settings()
        self.client_id = client_id or settings.reddit_client_id
        self.client_secret = client_secret or settings.reddit_client_secret
        self.user_agent = user_agent or 'StockSentimentBot/1.0'
        
        self.reddit = None
        if self.client_id and self.client_secret:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
        
        self.analyzer = SentimentAnalyzer()
        self.subreddits = ['wallstreetbets', 'stocks', 'investing', 'StockMarket']
    
    async def get_stock_posts(
        self, 
        symbol: str, 
        limit: int = 50
    ) -> list[SocialPost]:
        """Fetch Reddit posts mentioning a stock."""
        if not self.reddit:
            return []
        
        try:
            posts = []
            
            for subreddit_name in self.subreddits:
                subreddit = await asyncio.to_thread(
                    self.reddit.subreddit, 
                    subreddit_name
                )
                
                # Search for the stock symbol
                search_results = await asyncio.to_thread(
                    lambda: list(subreddit.search(
                        symbol, 
                        limit=limit // len(self.subreddits),
                        time_filter='week'
                    ))
                )
                
                for submission in search_results:
                    # Analyze sentiment
                    text = f"{submission.title} {submission.selftext}"
                    score, classification = self.analyzer.analyze(text)
                    
                    posts.append(SocialPost(
                        platform="reddit",
                        content=submission.title,
                        author=str(submission.author),
                        url=f"https://reddit.com{submission.permalink}",
                        created_at=datetime.fromtimestamp(submission.created_utc),
                        upvotes=submission.score,
                        comments=submission.num_comments,
                        sentiment_score=score,
                        sentiment_classification=classification
                    ))
            
            return posts
        except Exception as e:
            print(f"Error fetching Reddit posts: {e}")
            return []
    
    async def get_sentiment_analysis(self, symbol: str) -> Optional[SentimentAnalysis]:
        """Get overall Reddit sentiment for a stock."""
        posts = await self.get_stock_posts(symbol)
        
        if not posts:
            return None
        
        # Weight sentiment by upvotes
        total_weight = sum(max(p.upvotes, 1) for p in posts)
        weighted_score = sum(
            p.sentiment_score * max(p.upvotes, 1) for p in posts
        ) / total_weight if total_weight > 0 else 0
        
        # Determine classification
        if weighted_score <= -0.6:
            classification = SentimentScore.VERY_NEGATIVE
        elif weighted_score <= -0.2:
            classification = SentimentScore.NEGATIVE
        elif weighted_score < 0.2:
            classification = SentimentScore.NEUTRAL
        elif weighted_score < 0.6:
            classification = SentimentScore.POSITIVE
        else:
            classification = SentimentScore.VERY_POSITIVE
        
        return SentimentAnalysis(
            symbol=symbol,
            score=weighted_score,
            classification=classification,
            source=SentimentSource.REDDIT,
            confidence=min(len(posts) / 50.0, 1.0),
            sample_size=len(posts)
        )


class TwitterProvider:
    """Fetch and analyze Twitter sentiment (placeholder for now)."""
    
    def __init__(self):
        # Twitter API v2 requires elevated access
        # This is a placeholder for future implementation
        self.analyzer = SentimentAnalyzer()
    
    async def get_stock_tweets(self, symbol: str, limit: int = 50) -> list[SocialPost]:
        """Fetch tweets mentioning a stock."""
        # Placeholder - requires Twitter API credentials
        return []
    
    async def get_sentiment_analysis(self, symbol: str) -> Optional[SentimentAnalysis]:
        """Get overall Twitter sentiment for a stock."""
        # Placeholder
        return None
