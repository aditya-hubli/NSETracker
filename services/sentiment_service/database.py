"""Database operations for sentiment service."""
from datetime import datetime, timedelta
from typing import Optional

from supabase import Client

from .models import StockSentiment, TrendingStock


class SentimentDatabase:
    """Database operations for sentiment data."""
    
    def __init__(self, supabase_client: Client):
        self.db = supabase_client
    
    async def save_sentiment(self, sentiment: StockSentiment) -> None:
        """Save stock sentiment to database."""
        try:
            data = {
                "symbol": sentiment.symbol,
                "overall_score": sentiment.overall_score,
                "overall_classification": sentiment.overall_classification.value,
                "news_score": sentiment.news_sentiment.score if sentiment.news_sentiment else None,
                "reddit_score": sentiment.reddit_sentiment.score if sentiment.reddit_sentiment else None,
                "twitter_score": sentiment.twitter_sentiment.score if sentiment.twitter_sentiment else None,
                "trending_score": sentiment.trending_score,
                "last_updated": sentiment.last_updated.isoformat(),
            }
            
            # Upsert (insert or update)
            self.db.table("stock_sentiment").upsert(data).execute()
        except Exception as e:
            print(f"Error saving sentiment: {e}")
    
    async def get_sentiment(self, symbol: str) -> Optional[dict]:
        """Get latest sentiment for a stock."""
        try:
            result = (
                self.db.table("stock_sentiment")
                .select("*")
                .eq("symbol", symbol)
                .order("last_updated", desc=True)
                .limit(1)
                .execute()
            )
            
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            print(f"Error fetching sentiment: {e}")
            return None
    
    async def get_trending_stocks(self, limit: int = 10) -> list[TrendingStock]:
        """Get most trending stocks by sentiment and mentions."""
        try:
            # Get stocks updated in last 24 hours, ordered by trending score
            cutoff = (datetime.utcnow() - timedelta(hours=24)).isoformat()
            
            result = (
                self.db.table("stock_sentiment")
                .select("*")
                .gte("last_updated", cutoff)
                .order("trending_score", desc=True)
                .limit(limit)
                .execute()
            )
            
            trending = []
            for row in result.data:
                trending.append(TrendingStock(
                    symbol=row["symbol"],
                    mention_count=int(row.get("mention_count", 0)),
                    sentiment_score=row["overall_score"],
                    sentiment_classification=row["overall_classification"],
                    trending_score=row["trending_score"],
                ))
            
            return trending
        except Exception as e:
            print(f"Error fetching trending stocks: {e}")
            return []
    
    async def save_news_article(self, symbol: str, article: dict) -> None:
        """Save a news article."""
        try:
            data = {
                "symbol": symbol,
                "title": article["title"],
                "description": article.get("description"),
                "url": article["url"],
                "source": article["source"],
                "published_at": article["published_at"],
                "sentiment_score": article["sentiment_score"],
                "sentiment_classification": article["sentiment_classification"],
            }
            
            self.db.table("news_articles").insert(data).execute()
        except Exception as e:
            print(f"Error saving news article: {e}")
    
    async def save_social_post(self, symbol: str, post: dict) -> None:
        """Save a social media post."""
        try:
            data = {
                "symbol": symbol,
                "platform": post["platform"],
                "content": post["content"],
                "author": post["author"],
                "url": post.get("url"),
                "created_at": post["created_at"],
                "upvotes": post.get("upvotes", 0),
                "comments": post.get("comments", 0),
                "sentiment_score": post["sentiment_score"],
                "sentiment_classification": post["sentiment_classification"],
            }
            
            self.db.table("social_posts").insert(data).execute()
        except Exception as e:
            print(f"Error saving social post: {e}")
