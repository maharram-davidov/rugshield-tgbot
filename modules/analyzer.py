import aiohttp
import json
from typing import Dict, Any
import numpy as np
from transformers import pipeline
from web3 import Web3
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class TokenAnalyzer:
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('ETHEREUM_RPC_URL')))
        self.etherscan_api_key = os.getenv('ETHERSCAN_API_KEY')

    async def analyze(self, token_address: str) -> Dict[str, Any]:
        """
        Perform comprehensive AI analysis of a token.
        """
        try:
            # Gather token data
            token_data = await self._fetch_token_data(token_address)
            
            # Analyze token metrics
            metrics_analysis = self._analyze_metrics(token_data)
            
            # Analyze token description and social media presence
            text_analysis = self._analyze_text_data(token_data)
            
            # Generate risk assessment
            risk_assessment = self._assess_risk(token_data)
            
            # Return combined data
            return {
                "price": token_data.get("price", 0.0),
                "market_cap": token_data.get("market_cap", 0.0),
                "volume_24h": token_data.get("volume_24h", 0.0),
                "holders": token_data.get("holders", 0),
                "description": token_data.get("description", ""),
                "metrics": metrics_analysis,
                "text_analysis": text_analysis,
                "risk_assessment": risk_assessment
            }
        except Exception as e:
            return {
                "price": 0.0,
                "market_cap": 0.0,
                "volume_24h": 0.0,
                "holders": 0,
                "description": f"Error during analysis: {str(e)}",
                "metrics": {},
                "text_analysis": {},
                "risk_assessment": {}
            }

    async def _fetch_token_data(self, token_address: str) -> Dict[str, Any]:
        """
        Fetch token data from various sources.
        """
        try:
            # Validate address
            if not self.w3.is_address(token_address):
                raise ValueError("Invalid token address")

            # Get token contract
            token_contract = self.w3.eth.contract(
                address=token_address,
                abi=[]  # You would need to implement ABI fetching
            )

            # Get token data from DEX (example using Uniswap)
            async with aiohttp.ClientSession() as session:
                # First try to get token info from CoinGecko
                coingecko_url = f"https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses={token_address}&vs_currencies=usd&include_24hr_vol=true&include_market_cap=true"
                async with session.get(coingecko_url) as response:
                    if response.status == 200:
                        price_data = await response.json()
                        if token_address.lower() in price_data:
                            # Get token info from CoinGecko
                            token_info_url = f"https://api.coingecko.com/api/v3/coins/ethereum/contract/{token_address}"
                            async with session.get(token_info_url) as info_response:
                                if info_response.status == 200:
                                    token_info = await info_response.json()
                                    return {
                                        "price": price_data[token_address.lower()].get("usd", 0.0),
                                        "market_cap": price_data[token_address.lower()].get("usd_market_cap", 0.0),
                                        "volume_24h": price_data[token_address.lower()].get("usd_24h_vol", 0.0),
                                        "holders": await self._get_holder_count(token_address),
                                        "description": token_info.get("description", {}).get("en", "No description available"),
                                        "symbol": token_info.get("symbol", "").upper(),
                                        "name": token_info.get("name", "")
                                    }

                # If CoinGecko fails, try Etherscan
                etherscan_url = f"https://api.etherscan.io/api"
                params = {
                    "module": "token",
                    "action": "tokeninfo",
                    "contractaddress": token_address,
                    "apikey": self.etherscan_api_key
                }
                async with session.get(etherscan_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["status"] == "1" and data["message"] == "OK":
                            token_info = data["result"][0]
                            return {
                                "price": 0.0,  # You would need to implement price fetching
                                "market_cap": 0.0,
                                "volume_24h": 0.0,
                                "holders": await self._get_holder_count(token_address),
                                "description": token_info.get("description", "No description available"),
                                "symbol": token_info.get("symbol", "").upper(),
                                "name": token_info.get("name", "")
                            }

            # Fallback to basic data if all APIs fail
            return {
                "price": 0.0,
                "market_cap": 0.0,
                "volume_24h": 0.0,
                "holders": 0,
                "description": "No description available",
                "symbol": token_address[:6].upper(),  # Use first 6 chars of address as symbol
                "name": f"Token {token_address[:6]}"
            }
        except Exception as e:
            logger.error(f"Error fetching token data: {str(e)}")
            return {
                "price": 0.0,
                "market_cap": 0.0,
                "volume_24h": 0.0,
                "holders": 0,
                "description": f"Error fetching data: {str(e)}",
                "symbol": token_address[:6].upper(),
                "name": f"Token {token_address[:6]}"
            }

    async def _get_holder_count(self, token_address: str) -> int:
        """Get number of token holders using Etherscan API."""
        try:
            # First try to get holder count directly from Etherscan
            url = f"https://api.etherscan.io/api"
            params = {
                "module": "token",
                "action": "tokenholderlist",
                "contractaddress": token_address,
                "page": 1,
                "offset": 1,
                "apikey": self.etherscan_api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["status"] == "1" and data["message"] == "OK":
                            # Get total holders from the response
                            return int(data["result"][0]["TokenHolderCount"])
            
            # If direct method fails, try alternative method
            return await self._get_holder_count_alternative(token_address)
            
        except Exception as e:
            logger.error(f"Error getting holder count: {str(e)}")
            return await self._get_holder_count_alternative(token_address)

    async def _get_holder_count_alternative(self, token_address: str) -> int:
        """Alternative method to estimate holder count using transfer events."""
        try:
            # Get transfer events from Etherscan
            url = f"https://api.etherscan.io/api"
            params = {
                "module": "account",
                "action": "tokentx",
                "contractaddress": token_address,
                "page": 1,
                "offset": 1000,  # Get last 1000 transfers
                "sort": "desc",
                "apikey": self.etherscan_api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["status"] == "1" and data["message"] == "OK":
                            # Count unique addresses
                            unique_addresses = set()
                            for tx in data["result"]:
                                unique_addresses.add(tx["from"].lower())
                                unique_addresses.add(tx["to"].lower())
                            
                            # Remove zero address and contract address
                            unique_addresses.discard("0x0000000000000000000000000000000000000000")
                            unique_addresses.discard(token_address.lower())
                            
                            return len(unique_addresses)
            
            return 0
            
        except Exception as e:
            logger.error(f"Error in alternative holder count method: {str(e)}")
            return 0

    async def _get_token_description(self, token_address: str) -> str:
        """
        Get token description from various sources.
        """
        try:
            # This is a placeholder. You would need to implement actual description fetching
            # from sources like Etherscan, token websites, or social media
            return "No description available"
        except Exception:
            return "No description available"

    def _analyze_metrics(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze token metrics and market data.
        """
        try:
            price = token_data.get("price", 0.0)
            market_cap = token_data.get("market_cap", 0.0)
            volume_24h = token_data.get("volume_24h", 0.0)
            holders = token_data.get("holders", 0)

            # Price trend analysis
            price_trend = "neutral"
            if price > 0:
                if volume_24h > market_cap * 0.1:  # High volume relative to market cap
                    price_trend = "bullish"
                elif volume_24h < market_cap * 0.01:  # Low volume relative to market cap
                    price_trend = "bearish"

            # Volume analysis
            volume_analysis = "low"
            if volume_24h > 0:
                if volume_24h > market_cap * 0.5:  # High volume
                    volume_analysis = "high"
                elif volume_24h > market_cap * 0.1:  # Medium volume
                    volume_analysis = "medium"

            # Holder distribution analysis
            holder_distribution = "concentrated"
            if holders > 0:
                if holders > 10000:  # Large holder base
                    holder_distribution = "distributed"
                elif holders > 1000:  # Medium holder base
                    holder_distribution = "moderate"

            # Liquidity analysis
            liquidity_analysis = "insufficient"
            if market_cap > 0 and volume_24h > 0:
                liquidity_ratio = volume_24h / market_cap
                if liquidity_ratio > 0.5:  # High liquidity
                    liquidity_analysis = "high"
                elif liquidity_ratio > 0.1:  # Medium liquidity
                    liquidity_analysis = "medium"

            return {
                "price_trend": price_trend,
                "volume_analysis": volume_analysis,
                "holder_distribution": holder_distribution,
                "liquidity_analysis": liquidity_analysis,
                "raw_metrics": {
                    "price": price,
                    "market_cap": market_cap,
                    "volume_24h": volume_24h,
                    "holders": holders
                }
            }
        except Exception as e:
            print(f"Error in metrics analysis: {str(e)}")
            return {
                "price_trend": "unknown",
                "volume_analysis": "unknown",
                "holder_distribution": "unknown",
                "liquidity_analysis": "unknown",
                "raw_metrics": {}
            }

    def _analyze_text_data(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze token description and social media content.
        """
        try:
            description = token_data.get("description", "")
            
            # Basic sentiment analysis
            sentiment = "neutral"
            if description:
                # Simple keyword-based sentiment analysis
                positive_words = ["secure", "safe", "trusted", "verified", "audited", "reliable"]
                negative_words = ["scam", "fake", "suspicious", "unverified", "risky", "warning"]
                
                description_lower = description.lower()
                positive_count = sum(1 for word in positive_words if word in description_lower)
                negative_count = sum(1 for word in negative_words if word in description_lower)
                
                if positive_count > negative_count:
                    sentiment = "positive"
                elif negative_count > positive_count:
                    sentiment = "negative"

            # Credibility score calculation
            credibility_score = 0.5  # Default neutral score
            if description:
                # Factors affecting credibility:
                # 1. Description length (longer descriptions tend to be more credible)
                length_score = min(len(description) / 500, 1.0)  # Max score at 500 chars
                
                # 2. Presence of technical terms
                technical_terms = ["smart contract", "blockchain", "tokenomics", "liquidity", "audit"]
                technical_score = sum(1 for term in technical_terms if term in description_lower) / len(technical_terms)
                
                # 3. Presence of warning signs
                warning_terms = ["guaranteed", "100x", "moon", "get rich", "quick profit"]
                warning_score = 1 - (sum(1 for term in warning_terms if term in description_lower) / len(warning_terms))
                
                # Calculate final credibility score
                credibility_score = (length_score + technical_score + warning_score) / 3

            # Social media presence analysis
            social_media_presence = "low"
            if token_data.get("holders", 0) > 1000:
                social_media_presence = "high"
            elif token_data.get("holders", 0) > 100:
                social_media_presence = "medium"

            # Community engagement analysis
            community_engagement = "minimal"
            if token_data.get("volume_24h", 0) > token_data.get("market_cap", 1) * 0.1:
                community_engagement = "active"
            elif token_data.get("volume_24h", 0) > token_data.get("market_cap", 1) * 0.01:
                community_engagement = "moderate"

            return {
                "sentiment": sentiment,
                "credibility_score": credibility_score,
                "social_media_presence": social_media_presence,
                "community_engagement": community_engagement,
                "description_analysis": {
                    "length": len(description),
                    "has_technical_terms": any(term in description_lower for term in technical_terms),
                    "has_warning_signs": any(term in description_lower for term in warning_terms)
                }
            }
        except Exception as e:
            print(f"Error in text analysis: {str(e)}")
            return {
                "sentiment": "neutral",
                "credibility_score": 0.5,
                "social_media_presence": "low",
                "community_engagement": "minimal",
                "description_analysis": {}
            }

    def _assess_risk(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate risk assessment based on all available data.
        """
        try:
            risk_factors = []
            recommendations = []

            # Market cap risk
            market_cap = token_data.get("market_cap", 0.0)
            if market_cap < 100000:  # Less than $100k
                risk_factors.append("Very low market cap")
                recommendations.append("Extreme caution required")
            elif market_cap < 1000000:  # Less than $1M
                risk_factors.append("Low market cap")
                recommendations.append("High risk investment")

            # Volume risk
            volume_24h = token_data.get("volume_24h", 0.0)
            if volume_24h == 0:
                risk_factors.append("No trading volume")
                recommendations.append("Avoid trading")
            elif volume_24h < market_cap * 0.01:
                risk_factors.append("Low trading volume")
                recommendations.append("Limited liquidity")

            # Holder risk
            holders = token_data.get("holders", 0)
            if holders < 100:
                risk_factors.append("Very few holders")
                recommendations.append("High concentration risk")
            elif holders < 1000:
                risk_factors.append("Limited holder base")
                recommendations.append("Monitor holder distribution")

            # Liquidity risk
            if volume_24h > 0 and market_cap > 0:
                liquidity_ratio = volume_24h / market_cap
                if liquidity_ratio < 0.01:
                    risk_factors.append("Low liquidity")
                    recommendations.append("Check liquidity before trading")
                elif liquidity_ratio < 0.1:
                    risk_factors.append("Moderate liquidity")
                    recommendations.append("Monitor liquidity changes")

            # Overall risk assessment
            risk_score = len(risk_factors)
            if risk_score >= 4:
                overall_risk = "extreme"
            elif risk_score >= 3:
                overall_risk = "high"
            elif risk_score >= 2:
                overall_risk = "medium"
            elif risk_score >= 1:
                overall_risk = "low"
            else:
                overall_risk = "minimal"

            return {
                "overall_risk": overall_risk,
                "risk_factors": risk_factors,
                "recommendations": recommendations,
                "risk_metrics": {
                    "market_cap_risk": market_cap < 1000000,
                    "volume_risk": volume_24h < market_cap * 0.01,
                    "holder_risk": holders < 1000,
                    "liquidity_risk": volume_24h > 0 and (volume_24h / market_cap) < 0.1
                }
            }
        except Exception as e:
            print(f"Error in risk assessment: {str(e)}")
            return {
                "overall_risk": "unknown",
                "risk_factors": ["Error in risk assessment"],
                "recommendations": ["Unable to generate recommendations"],
                "risk_metrics": {}
            } 