import feedparser
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from agent.utils.logger import setup_logger
from agent.utils.config import Config

logger = setup_logger(__name__)


class NewsAggregator:
    def __init__(self):
        self.config = Config()
        self.news_sources = [
            'https://cointelegraph.com/rss',
            'https://decrypt.co/feed',
            'https://www.coindesk.com/arc/outboundfeeds/rss/',
        ]
    
    def fetch_funding_news(self, category: str, days_back: int = 30) -> List[Dict]:
        logger.info(f"Fetching funding news for {category} from last {days_back} days")
        
        all_news = []
        from dateutil import tz
        cutoff_date = datetime.now(tz.tzutc()) - timedelta(days=days_back)
        
        for source in self.news_sources:
            try:
                logger.debug(f"Fetching from: {source}")
                feed = feedparser.parse(source)
                
                for entry in feed.entries:
                    if self._is_funding_related(entry, category):
                        published = self._parse_date(entry.get('published', ''))
                        
                        if published and published > cutoff_date:
                            all_news.append({
                                'title': entry.get('title', ''),
                                'link': entry.get('link', ''),
                                'published': published.isoformat(),
                                'source': source,
                                'summary': entry.get('summary', '')
                            })
            except Exception as e:
                logger.error(f"Error fetching news from {source}: {str(e)}")
        
        logger.info(f"Found {len(all_news)} relevant funding news articles")
        return all_news
    
    def _is_funding_related(self, entry: Dict, category: str) -> bool:
        funding_keywords = ['funding', 'raises', 'investment', 'series', 'round', 'capital', 'venture']
        category_keywords = [category.lower(), 'blockchain', 'crypto', 'web3', 'defi']
        
        text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
        
        has_funding = any(keyword in text for keyword in funding_keywords)
        has_category = any(keyword in text for keyword in category_keywords)
        
        return has_funding and has_category
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        try:
            from dateutil import parser, tz
            parsed = parser.parse(date_str)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=tz.tzutc())
            return parsed
        except:
            return None
    
    def extract_companies_from_news(self, news_articles: List[Dict]) -> List[str]:
        companies = []
        
        for article in news_articles:
            title = article.get('title', '')
            
            for word in title.split():
                if word[0].isupper() and len(word) > 3:
                    companies.append(word)
        
        return list(set(companies))
