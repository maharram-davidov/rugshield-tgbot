import tweepy
import aiohttp
from typing import Dict, Any, List
from textblob import TextBlob
import os
from dotenv import load_dotenv

load_dotenv()

class SentimentAnalyzer:
    def __init__(self):
        # Initialize Twitter API client
        self.twitter_client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        )

    async def get_sentiment(self, token_symbol: str) -> str:
        """
        Analyze social media sentiment for a given token.
        """
        try:
            # Gather social media data
            twitter_data = await self._get_twitter_sentiment(token_symbol)
            reddit_data = await self._get_reddit_sentiment(token_symbol)
            telegram_data = await self._get_telegram_sentiment(token_symbol)

            # Combine and analyze sentiment
            overall_sentiment = self._analyze_overall_sentiment(
                twitter_data, reddit_data, telegram_data
            )

            return self._format_sentiment_analysis(
                token_symbol, twitter_data, reddit_data, telegram_data, overall_sentiment
            )
        except Exception as e:
            return f"Error analyzing sentiment: {str(e)}"

    async def _get_twitter_sentiment(self, token_symbol: str) -> Dict[str, Any]:
        """
        Analyze Twitter sentiment for the token.
        """
        try:
            # Search for tweets about the token
            tweets = self.twitter_client.search_recent_tweets(
                query=f"#{token_symbol} OR ${token_symbol}",
                max_results=100
            )

            if not tweets.data:
                return {
                    "sentiment": "neutral",
                    "score": 0.0,
                    "volume": 0,
                    "trending": False
                }

            # Analyze tweet sentiment
            sentiments = [TextBlob(tweet.text).sentiment.polarity for tweet in tweets.data]
            avg_sentiment = sum(sentiments) / len(sentiments)

            return {
                "sentiment": self._get_sentiment_label(avg_sentiment),
                "score": avg_sentiment,
                "volume": len(tweets.data),
                "trending": len(tweets.data) > 50
            }
        except Exception:
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "volume": 0,
                "trending": False
            }

    async def _get_reddit_sentiment(self, token_symbol: str) -> Dict[str, Any]:
        """
        Analyze Reddit sentiment for the token.
        """
        # Implement Reddit API integration
        return {
            "sentiment": "neutral",
            "score": 0.0,
            "volume": 0,
            "trending": False
        }

    async def _get_telegram_sentiment(self, token_symbol: str) -> Dict[str, Any]:
        """
        Analyze Telegram sentiment for the token.
        """
        # Implement Telegram channel analysis
        return {
            "sentiment": "neutral",
            "score": 0.0,
            "volume": 0,
            "trending": False
        }

    def _analyze_overall_sentiment(
        self,
        twitter_data: Dict[str, Any],
        reddit_data: Dict[str, Any],
        telegram_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate overall sentiment across all platforms.
        """
        # Calculate weighted average sentiment
        total_volume = (
            twitter_data["volume"] +
            reddit_data["volume"] +
            telegram_data["volume"]
        )

        if total_volume == 0:
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "confidence": "low"
            }

        weighted_score = (
            twitter_data["score"] * twitter_data["volume"] +
            reddit_data["score"] * reddit_data["volume"] +
            telegram_data["score"] * telegram_data["volume"]
        ) / total_volume

        return {
            "sentiment": self._get_sentiment_label(weighted_score),
            "score": weighted_score,
            "confidence": "high" if total_volume > 100 else "low"
        }

    def _get_sentiment_label(self, score: float) -> str:
        """
        Convert sentiment score to label.
        """
        if score > 0.2:
            return "positive"
        elif score < -0.2:
            return "negative"
        return "neutral"

    def _format_sentiment_analysis(
        self,
        token_symbol: str,
        twitter_data: Dict[str, Any],
        reddit_data: Dict[str, Any],
        telegram_data: Dict[str, Any],
        overall_sentiment: Dict[str, Any]
    ) -> str:
        """
        Format sentiment analysis results.
        """
        return f"""
📊 Social Media Sentiment Analysis for {token_symbol}

🐦 Twitter:
• Sentiment: {twitter_data['sentiment'].title()}
• Volume: {twitter_data['volume']} mentions
• Trending: {'Yes' if twitter_data['trending'] else 'No'}

📱 Reddit:
• Sentiment: {reddit_data['sentiment'].title()}
• Volume: {reddit_data['volume']} mentions
• Trending: {'Yes' if reddit_data['trending'] else 'No'}

💬 Telegram:
• Sentiment: {telegram_data['sentiment'].title()}
• Volume: {telegram_data['volume']} mentions
• Trending: {'Yes' if telegram_data['trending'] else 'No'}

📈 Overall Sentiment:
• Sentiment: {overall_sentiment['sentiment'].title()}
• Confidence: {overall_sentiment['confidence'].title()}
• Score: {overall_sentiment['score']:.2f}
""" 