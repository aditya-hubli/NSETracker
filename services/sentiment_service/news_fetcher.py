"""
News Fetcher for Sentiment Analysis

Fetches news articles for stocks from various sources.

Current: Uses yfinance news API and Google News RSS
Future: Add dedicated Indian news APIs (Economic Times, Moneycontrol, etc.)
"""

import httpx
import asyncio
from typing import List, Optional
from datetime import datetime, timedelta
import yfinance as yf
import re
from urllib.parse import quote

from .models import NewsArticle, NewsSource


class NewsFetcher:
    """
    Fetches news articles from multiple sources.
    
    Sources:
    - yfinance news API (default)
    - Google News RSS (backup)
    - Future: Economic Times, Moneycontrol APIs
    """
    
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def fetch_news(
        self,
        symbol: str,
        max_articles: int = 10,
        days_back: int = 7
    ) -> List[NewsArticle]:
        """
        Fetch news articles for a stock symbol.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE.NS")
            max_articles: Maximum number of articles to fetch
            days_back: How many days back to search
            
        Returns:
            List of NewsArticle objects
        """
        articles = []
        
        # Try yfinance first
        yf_articles = await self._fetch_yfinance_news(symbol, max_articles)
        articles.extend(yf_articles)
        
        # If not enough articles, try Google News
        if len(articles) < max_articles:
            company_name = self._get_company_name(symbol)
            google_articles = await self._fetch_google_news(
                company_name,
                max_articles - len(articles)
            )
            articles.extend(google_articles)
        
        # Sort by date and limit
        articles.sort(key=lambda x: x.published_at or datetime.min, reverse=True)
        return articles[:max_articles]
    
    async def _fetch_yfinance_news(
        self,
        symbol: str,
        max_articles: int
    ) -> List[NewsArticle]:
        """Fetch news from yfinance"""
        articles = []
        
        try:
            print(f"Fetching yfinance news for {symbol}...")
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            print(f"yfinance returned {len(news) if news else 0} articles for {symbol}")
            
            if news:
                for item in news[:max_articles]:
                    # Handle new yfinance format (nested content)
                    content = item.get('content', item)
                    
                    # Get title
                    title = content.get('title', '') or item.get('title', '')
                    
                    # Get summary
                    summary = content.get('summary', '') or content.get('description', '') or item.get('summary', '')
                    
                    # Get URL
                    url = None
                    if 'canonicalUrl' in content:
                        url = content['canonicalUrl'].get('url')
                    elif 'clickThroughUrl' in content:
                        url = content['clickThroughUrl'].get('url')
                    else:
                        url = item.get('link')
                    
                    # Get publish date
                    pub_date = None
                    pub_time = content.get('pubDate') or item.get('providerPublishTime')
                    if pub_time:
                        if isinstance(pub_time, str):
                            try:
                                pub_date = datetime.fromisoformat(pub_time.replace('Z', '+00:00'))
                            except:
                                pass
                        elif isinstance(pub_time, (int, float)):
                            pub_date = datetime.fromtimestamp(pub_time)
                    
                    # Get source
                    source = 'Unknown'
                    if 'provider' in content:
                        source = content['provider'].get('displayName', 'Unknown')
                    else:
                        source = item.get('publisher', 'Unknown')
                    
                    if title:  # Only add if we have a title
                        article = NewsArticle(
                            title=title,
                            source=source,
                            url=url,
                            published_at=pub_date,
                            summary=summary[:500] if summary else None
                        )
                        articles.append(article)
        except Exception as e:
            print(f"Error fetching yfinance news for {symbol}: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"Returning {len(articles)} articles from yfinance for {symbol}")
        return articles
    
    async def _fetch_google_news(
        self,
        query: str,
        max_articles: int
    ) -> List[NewsArticle]:
        """
        Fetch news from Google News RSS.
        
        Note: This is a simple implementation.
        For production, consider using official news APIs.
        """
        articles = []
        
        try:
            print(f"Fetching Google News for query: {query}")
            client = await self._get_client()
            encoded_query = quote(f"{query} stock NSE BSE")
            url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
            
            response = await client.get(url)
            print(f"Google News response status: {response.status_code}")
            if response.status_code == 200:
                text = response.text
                articles = self._parse_rss(text, max_articles)
                print(f"Parsed {len(articles)} articles from Google News")
        except Exception as e:
            print(f"Error fetching Google News for {query}: {e}")
            import traceback
            traceback.print_exc()
        
        return articles
    
    def _parse_rss(self, rss_text: str, max_articles: int) -> List[NewsArticle]:
        """Parse RSS feed XML"""
        articles = []
        
        # Simple regex-based parsing (for robustness without xml library)
        title_pattern = r'<title><!\[CDATA\[(.*?)\]\]></title>|<title>(.*?)</title>'
        link_pattern = r'<link>(.*?)</link>'
        pubdate_pattern = r'<pubDate>(.*?)</pubDate>'
        source_pattern = r'<source.*?>(.*?)</source>'
        
        items = rss_text.split('<item>')[1:]  # Skip channel info
        
        for item in items[:max_articles]:
            try:
                # Extract title
                title_match = re.search(title_pattern, item)
                title = (title_match.group(1) or title_match.group(2)) if title_match else ""
                
                # Extract link
                link_match = re.search(link_pattern, item)
                link = link_match.group(1) if link_match else None
                
                # Extract source
                source_match = re.search(source_pattern, item)
                source = source_match.group(1) if source_match else "Google News"
                
                # Extract date
                date_match = re.search(pubdate_pattern, item)
                pub_date = None
                if date_match:
                    try:
                        from email.utils import parsedate_to_datetime
                        pub_date = parsedate_to_datetime(date_match.group(1))
                    except:
                        pass
                
                if title:
                    articles.append(NewsArticle(
                        title=title.strip(),
                        source=source,
                        url=link,
                        published_at=pub_date
                    ))
            except Exception:
                continue
        
        return articles
    
    def _get_company_name(self, symbol: str) -> str:
        """Get company name from symbol"""
        # Remove exchange suffix
        clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
        
        # Common Indian stock names
        company_names = {
            'RELIANCE': 'Reliance Industries',
            'TCS': 'Tata Consultancy Services',
            'HDFCBANK': 'HDFC Bank',
            'INFY': 'Infosys',
            'ICICIBANK': 'ICICI Bank',
            'HINDUNILVR': 'Hindustan Unilever',
            'ITC': 'ITC Limited',
            'SBIN': 'State Bank of India',
            'BHARTIARTL': 'Bharti Airtel',
            'KOTAKBANK': 'Kotak Mahindra Bank',
            'AXISBANK': 'Axis Bank',
            'LT': 'Larsen & Toubro',
            'WIPRO': 'Wipro',
            'HCLTECH': 'HCL Technologies',
            'MARUTI': 'Maruti Suzuki',
            'TATAMOTORS': 'Tata Motors',
            'TATASTEEL': 'Tata Steel',
            'SUNPHARMA': 'Sun Pharmaceutical',
            'BAJFINANCE': 'Bajaj Finance',
            'ASIANPAINT': 'Asian Paints',
        }
        
        return company_names.get(clean_symbol, clean_symbol)
    
    async def fetch_market_news(self, max_articles: int = 20) -> List[NewsArticle]:
        """Fetch general Indian market news"""
        queries = [
            "NSE Nifty market",
            "BSE Sensex stock market India",
            "Indian stock market today"
        ]
        
        all_articles = []
        for query in queries:
            articles = await self._fetch_google_news(query, max_articles // len(queries))
            all_articles.extend(articles)
        
        # Deduplicate by title
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            if article.title not in seen_titles:
                seen_titles.add(article.title)
                unique_articles.append(article)
        
        return unique_articles[:max_articles]
