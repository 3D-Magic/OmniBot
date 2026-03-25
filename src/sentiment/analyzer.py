"""
OMNIBOT Sentiment Analyzer
Analyzes market sentiment from free sources
"""

import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict

from config.settings import SENTIMENT

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyzes market sentiment from Reddit and RSS feeds"""

    def __init__(self):
        self.enabled = SENTIMENT.get('enabled', True)
        self.sources = SENTIMENT.get('sources', [])
        self.subreddits = SENTIMENT.get('reddit_subreddits', [])
        self.rss_feeds = SENTIMENT.get('rss_feeds', [])
        self.update_interval = SENTIMENT.get('update_interval_minutes', 30)
        self.min_mentions = SENTIMENT.get('min_mentions', 5)

        self.cache: Dict[str, Any] = {}
        self.last_update: Optional[datetime] = None

        logger.info(f"SentimentAnalyzer initialized (sources: {self.sources})")

    def _analyze_text(self, text: str) -> float:
        """Simple sentiment analysis using keyword matching"""
        text = text.lower()

        positive_words = ['bull', 'bullish', 'moon', 'rocket', 'gain', 'profit', 
                         'up', 'rise', 'rising', 'growth', 'buy', 'long', 'calls']
        negative_words = ['bear', 'bearish', 'crash', 'dump', 'loss', 'lose',
                         'down', 'fall', 'falling', 'sell', 'short', 'puts', 'panic']

        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)

        total = pos_count + neg_count
        if total == 0:
            return 0.0

        return (pos_count - neg_count) / total

    def fetch_reddit_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Fetch sentiment from Reddit (mock implementation)"""
        # In production, use praw library with proper API credentials
        # This is a simplified version

        mentions = defaultdict(list)

        # Mock data for demonstration
        mock_posts = [
            f"{symbol} looking bullish today! 🚀",
            f"Should I buy {symbol}?",
            f"{symbol} earnings coming up",
        ]

        sentiments = []
        for post in mock_posts:
            sentiment = self._analyze_text(post)
            sentiments.append(sentiment)

        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

        return {
            'source': 'reddit',
            'mentions': len(mock_posts),
            'avg_sentiment': avg_sentiment,
            'bullish_ratio': sum(1 for s in sentiments if s > 0) / len(sentiments) if sentiments else 0,
            'timestamp': datetime.now().isoformat()
        }

    def fetch_rss_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Fetch sentiment from RSS feeds"""
        try:
            import feedparser

            all_entries = []
            for feed_url in self.rss_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    all_entries.extend(feed.entries[:10])  # Last 10 entries
                except Exception as e:
                    logger.warning(f"Failed to parse RSS feed {feed_url}: {e}")

            # Filter for symbol mentions
            symbol_mentions = []
            for entry in all_entries:
                title = entry.get('title', '')
                summary = entry.get('summary', '')

                if symbol.upper() in title.upper() or symbol.upper() in summary.upper():
                    text = f"{title} {summary}"
                    sentiment = self._analyze_text(text)
                    symbol_mentions.append({
                        'title': title,
                        'sentiment': sentiment,
                        'published': entry.get('published', '')
                    })

            if symbol_mentions:
                avg_sentiment = sum(m['sentiment'] for m in symbol_mentions) / len(symbol_mentions)
            else:
                avg_sentiment = 0

            return {
                'source': 'rss',
                'mentions': len(symbol_mentions),
                'avg_sentiment': avg_sentiment,
                'articles': symbol_mentions[:5],  # Top 5
                'timestamp': datetime.now().isoformat()
            }

        except ImportError:
            logger.warning("feedparser not installed")
            return {'source': 'rss', 'mentions': 0, 'avg_sentiment': 0}

    def analyze_symbol(self, symbol: str) -> Dict[str, Any]:
        """Analyze sentiment for a specific symbol"""
        if not self.enabled:
            return {'enabled': False}

        results = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'sources': {}
        }

        total_sentiment = 0
        source_count = 0

        if 'reddit' in self.sources:
            reddit_data = self.fetch_reddit_sentiment(symbol)
            results['sources']['reddit'] = reddit_data
            if reddit_data['mentions'] >= self.min_mentions:
                total_sentiment += reddit_data['avg_sentiment']
                source_count += 1

        if 'rss' in self.sources:
            rss_data = self.fetch_rss_sentiment(symbol)
            results['sources']['rss'] = rss_data
            if rss_data['mentions'] >= self.min_mentions:
                total_sentiment += rss_data['avg_sentiment']
                source_count += 1

        # Calculate overall sentiment
        if source_count > 0:
            overall = total_sentiment / source_count
        else:
            overall = 0

        results['overall_sentiment'] = overall
        results['sentiment_label'] = self._label_sentiment(overall)

        return results

    def _label_sentiment(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.3:
            return "very_bullish"
        elif score > 0.1:
            return "bullish"
        elif score < -0.3:
            return "very_bearish"
        elif score < -0.1:
            return "bearish"
        else:
            return "neutral"

    def get_market_sentiment(self) -> Dict[str, Any]:
        """Get overall market sentiment"""
        # Analyze SPY as market proxy
        return self.analyze_symbol("SPY")


def create_sentiment_analyzer() -> SentimentAnalyzer:
    """Factory function"""
    return SentimentAnalyzer()
