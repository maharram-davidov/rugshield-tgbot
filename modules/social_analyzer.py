import aiohttp
from typing import Dict, Any
import os
from dotenv import load_dotenv
import logging
import json
from datetime import datetime, timedelta

load_dotenv()
logger = logging.getLogger(__name__)

class SocialAnalyzer:
    def __init__(self):
        self.twitter_api_key = os.getenv('TWITTER_API_KEY')

    async def analyze(self, token_address: str, token_ticker: str = None) -> Dict[str, Any]:
        """Analyze social media presence and sentiment for a token using Twitter data."""
        try:
            # Get Twitter data using token ticker
            twitter_data = await self._get_twitter_data(token_ticker or token_address)

            # Calculate engagement metrics
            total_mentions = twitter_data['mentions']

            # Determine activity level
            activity_level = self._determine_activity_level(total_mentions)

            return {
                "twitter_mentions": twitter_data['mentions'],
                "sentiment_score": twitter_data['sentiment'],
                "activity_level": activity_level,
                "platform_data": {
                    "twitter": twitter_data
                }
            }
        except Exception as e:
            logger.error(f"Error in social analysis: {str(e)}")
            return self._get_default_data()

    async def _get_twitter_data(self, token_identifier: str) -> Dict[str, Any]:
        """Get Twitter data for the token."""
        try:
            # Twitter API v2 endpoint
            url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {"Authorization": f"Bearer {self.twitter_api_key}"}
            
            # Build search query using token ticker
            query = f"#{token_identifier} OR ${token_identifier}"
            if len(token_identifier) > 3:  # If it's a contract address, also search for common variations
                query += f" OR {token_identifier[:6]}...{token_identifier[-4:]}"
            
            params = {
                "query": query,
                "max_results": 100,
                "tweet.fields": "created_at,public_metrics,lang",
                "expansions": "author_id",
                "user.fields": "public_metrics"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        tweets = data.get('data', [])
                        users = {user['id']: user for user in data.get('includes', {}).get('users', [])}
                        
                        # Calculate metrics
                        mentions = len(tweets)
                        engagement = sum(tweet['public_metrics']['retweet_count'] + 
                                      tweet['public_metrics']['reply_count'] + 
                                      tweet['public_metrics']['like_count'] 
                                      for tweet in tweets)
                        
                        # Calculate sentiment
                        sentiment = self._analyze_twitter_sentiment(tweets)
                        
                        # Format tweets with user info
                        formatted_tweets = []
                        for tweet in tweets[:5]:  # Get 5 most recent tweets
                            user = users.get(tweet['author_id'], {})
                            formatted_tweet = {
                                'text': tweet['text'],
                                'created_at': tweet['created_at'],
                                'public_metrics': tweet['public_metrics'],
                                'author': {
                                    'username': user.get('username', ''),
                                    'followers': user.get('public_metrics', {}).get('followers_count', 0)
                                }
                            }
                            formatted_tweets.append(formatted_tweet)
                        
                        return {
                            "mentions": mentions,
                            "engagement": engagement,
                            "sentiment": sentiment,
                            "recent_tweets": formatted_tweets
                        }

            return self._get_default_platform_data()
        except Exception as e:
            logger.error(f"Error fetching Twitter data: {str(e)}")
            return self._get_default_platform_data()

    def _determine_activity_level(self, total_mentions: int) -> str:
        """Determine the activity level based on total mentions."""
        if total_mentions > 1000:
            return "very_high"
        elif total_mentions > 500:
            return "high"
        elif total_mentions > 100:
            return "medium"
        elif total_mentions > 10:
            return "low"
        else:
            return "very_low"

    def _analyze_twitter_sentiment(self, tweets: list) -> float:
        """Analyze sentiment of Twitter posts."""
        if not tweets:
            return 0.5  # Neutral sentiment

        # Simple sentiment analysis based on engagement metrics
        total_engagement = sum(
            tweet['public_metrics']['retweet_count'] +
            tweet['public_metrics']['reply_count'] +
            tweet['public_metrics']['like_count']
            for tweet in tweets
        )
        
        # Normalize sentiment between 0 and 1
        return min(total_engagement / (len(tweets) * 100), 1.0)

    def _get_default_platform_data(self) -> Dict[str, Any]:
        """Get default data structure for a platform."""
        return {
            "mentions": 0,
            "engagement": 0,
            "sentiment": 0.5,
            "recent_tweets": []
        }

    def _get_default_data(self) -> Dict[str, Any]:
        """Get default data structure for social analysis."""
        return {
            "twitter_mentions": 0,
            "sentiment_score": 0.5,
            "activity_level": "very_low",
            "platform_data": {
                "twitter": self._get_default_platform_data()
            }
        } 