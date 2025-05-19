import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import aiohttp
from dotenv import load_dotenv
import tweepy

load_dotenv()

class ScamDatabase:
    def __init__(self):
        self.db_file = "data/scam_database.json"
        self.ensure_db_exists()
        self.scam_data = self.load_database()
        
        # Initialize Twitter client
        self.twitter_client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        )

    def ensure_db_exists(self):
        """
        Ensure the database file and directory exist.
        """
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                json.dump({
                    "scam_tokens": {},
                    "suspicious_addresses": {},
                    "known_scammers": {},
                    "last_updated": datetime.now().isoformat()
                }, f, indent=4)

    def load_database(self) -> Dict[str, Any]:
        """
        Load the scam database from file.
        """
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading database: {str(e)}")
            return {
                "scam_tokens": {},
                "suspicious_addresses": {},
                "known_scammers": {},
                "last_updated": datetime.now().isoformat()
            }

    def save_database(self):
        """
        Save the scam database to file.
        """
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.scam_data, f, indent=4)
        except Exception as e:
            print(f"Error saving database: {str(e)}")

    async def check_token(self, token_address: str) -> str:
        """
        Check if a token is in the scam database.
        """
        try:
            # Check if token is in database
            if token_address in self.scam_data["scam_tokens"]:
                return self._format_scam_report(self.scam_data["scam_tokens"][token_address])
            
            # Check if token is suspicious
            if token_address in self.scam_data["suspicious_addresses"]:
                return self._format_suspicious_report(self.scam_data["suspicious_addresses"][token_address])
            
            # Check for new scam reports
            new_report = await self._check_external_sources(token_address)
            if new_report:
                self._add_to_database(token_address, new_report)
                return self._format_scam_report(new_report)
            
            return "✅ Token not found in scam database. However, always DYOR!"
        except Exception as e:
            return f"Error checking scam database: {str(e)}"

    async def _check_external_sources(self, token_address: str) -> Optional[Dict[str, Any]]:
        """
        Check external sources for scam reports.
        """
        # This is a placeholder implementation
        # You would need to implement actual external source checking
        return None

    def _add_to_database(self, token_address: str, report: Dict[str, Any]):
        """
        Add a new scam report to the database.
        """
        self.scam_data["scam_tokens"][token_address] = {
            **report,
            "added_date": datetime.now().isoformat()
        }
        self.save_database()

    def _format_scam_report(self, report: Dict[str, Any]) -> str:
        """
        Format a scam report for display.
        """
        return f"""
⚠️ SCAM ALERT ⚠️

Token has been reported as a scam!

📋 Report Details:
• Type: {report.get('type', 'Unknown')}
• Severity: {report.get('severity', 'Unknown')}
• Reported Date: {report.get('reported_date', 'Unknown')}
• Source: {report.get('source', 'Unknown')}

🔍 Description:
{report.get('description', 'No description available')}

⚠️ Warning Signs:
{chr(10).join(f'• {sign}' for sign in report.get('warning_signs', ['No warning signs listed']))}

💡 Recommendations:
{chr(10).join(f'• {rec}' for rec in report.get('recommendations', ['No recommendations available']))}
"""

    def _format_suspicious_report(self, report: Dict[str, Any]) -> str:
        """
        Format a suspicious activity report for display.
        """
        return f"""
⚠️ SUSPICIOUS ACTIVITY DETECTED

Token shows suspicious patterns!

📋 Suspicious Indicators:
{chr(10).join(f'• {indicator}' for indicator in report.get('indicators', ['No indicators listed']))}

🔍 Details:
{report.get('details', 'No details available')}

💡 Recommendations:
{chr(10).join(f'• {rec}' for rec in report.get('recommendations', ['No recommendations available']))}
"""

    async def add_scam_report(
        self,
        token_address: str,
        report_type: str,
        severity: str,
        description: str,
        warning_signs: List[str],
        recommendations: List[str],
        source: str
    ) -> bool:
        """
        Add a new scam report to the database.
        """
        try:
            report = {
                "type": report_type,
                "severity": severity,
                "description": description,
                "warning_signs": warning_signs,
                "recommendations": recommendations,
                "source": source,
                "reported_date": datetime.now().isoformat()
            }
            
            self._add_to_database(token_address, report)
            return True
        except Exception as e:
            print(f"Error adding scam report: {str(e)}")
            return False

    async def add_suspicious_address(
        self,
        address: str,
        indicators: List[str],
        details: str,
        recommendations: List[str]
    ) -> bool:
        """
        Add a new suspicious address to the database.
        """
        try:
            self.scam_data["suspicious_addresses"][address] = {
                "indicators": indicators,
                "details": details,
                "recommendations": recommendations,
                "added_date": datetime.now().isoformat()
            }
            self.save_database()
            return True
        except Exception as e:
            print(f"Error adding suspicious address: {str(e)}")
            return False

    async def report_to_twitter(
        self,
        token_address: str,
        scam_type: str,
        description: str,
        warning_signs: List[str],
        evidence: Optional[str] = None
    ) -> bool:
        """
        Report a scam token to Twitter.
        """
        try:
            # Format the tweet
            tweet_text = self._format_scam_tweet(
                token_address,
                scam_type,
                description,
                warning_signs,
                evidence
            )
            
            # Post the tweet
            response = self.twitter_client.create_tweet(text=tweet_text)
            
            # Add the tweet ID to the scam report
            if response and response.data:
                tweet_id = response.data['id']
                self._add_tweet_reference(token_address, tweet_id)
                return True
            
            return False
        except Exception as e:
            print(f"Error reporting to Twitter: {str(e)}")
            return False

    def _format_scam_tweet(
        self,
        token_address: str,
        scam_type: str,
        description: str,
        warning_signs: List[str],
        evidence: Optional[str]
    ) -> str:
        """
        Format the scam report as a tweet.
        """
        # Format warning signs
        warning_text = "\n".join([f"⚠️ {sign}" for sign in warning_signs[:3]])  # Limit to 3 signs
        
        # Format the tweet
        tweet = f"""
🚨 SCAM ALERT 🚨

Token: {token_address}
Type: {scam_type}

{description}

{warning_text}

🔍 Evidence: {evidence if evidence else "Available upon request"}

#CryptoScam #ScamAlert #Crypto #Blockchain
"""
        # Ensure tweet is within Twitter's character limit (280)
        return tweet[:280]

    def _add_tweet_reference(self, token_address: str, tweet_id: str):
        """
        Add Twitter reference to the scam report.
        """
        if token_address in self.scam_data["scam_tokens"]:
            self.scam_data["scam_tokens"][token_address]["twitter_reports"] = self.scam_data["scam_tokens"][token_address].get("twitter_reports", []) + [tweet_id]
            self.save_database()

    async def report_suspicious_activity(
        self,
        token_address: str,
        activity_type: str,
        description: str,
        evidence: Optional[str] = None
    ) -> bool:
        """
        Report suspicious activity to Twitter.
        """
        try:
            # Format the tweet
            tweet_text = f"""
⚠️ SUSPICIOUS ACTIVITY DETECTED ⚠️

Token: {token_address}
Type: {activity_type}

{description}

🔍 Evidence: {evidence if evidence else "Available upon request"}

#CryptoAlert #Crypto #Blockchain
"""
            # Ensure tweet is within Twitter's character limit
            tweet_text = tweet_text[:280]
            
            # Post the tweet
            response = self.twitter_client.create_tweet(text=tweet_text)
            
            if response and response.data:
                tweet_id = response.data['id']
                self._add_tweet_reference(token_address, tweet_id)
                return True
            
            return False
        except Exception as e:
            print(f"Error reporting suspicious activity: {str(e)}")
            return False

    async def update_scam_report(
        self,
        token_address: str,
        update_type: str,
        new_information: str
    ) -> bool:
        """
        Update an existing scam report on Twitter.
        """
        try:
            if token_address not in self.scam_data["scam_tokens"]:
                return False
            
            # Format the update tweet
            tweet_text = f"""
🔄 SCAM UPDATE 🔄

Token: {token_address}
Update: {update_type}

{new_information}

#CryptoScam #ScamAlert #Crypto #Blockchain
"""
            # Ensure tweet is within Twitter's character limit
            tweet_text = tweet_text[:280]
            
            # Post the update tweet
            response = self.twitter_client.create_tweet(text=tweet_text)
            
            if response and response.data:
                tweet_id = response.data['id']
                self._add_tweet_reference(token_address, tweet_id)
                return True
            
            return False
        except Exception as e:
            print(f"Error updating scam report: {str(e)}")
            return False 