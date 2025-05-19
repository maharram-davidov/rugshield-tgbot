from web3 import Web3
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta

load_dotenv()

class WalletAnalyzer:
    def __init__(self):
        # Initialize Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('ETHEREUM_RPC_URL')))
        
        # Known scammer addresses (you would need to maintain this list)
        self.known_scammer_addresses = set()

    async def analyze(self, wallet_address: str) -> str:
        """
        Analyze wallet behavior and transactions.
        """
        try:
            # Validate address
            if not self.w3.is_address(wallet_address):
                return "Invalid wallet address provided."

            # Get wallet data
            wallet_data = await self._get_wallet_data(wallet_address)
            
            # Analyze transactions
            transaction_analysis = self._analyze_transactions(wallet_data["transactions"])
            
            # Analyze token holdings
            holdings_analysis = self._analyze_holdings(wallet_data["holdings"])
            
            # Check for suspicious activity
            suspicious_activity = self._check_suspicious_activity(wallet_data)
            
            return self._format_analysis(
                wallet_address,
                wallet_data,
                transaction_analysis,
                holdings_analysis,
                suspicious_activity
            )
        except Exception as e:
            return f"Error analyzing wallet: {str(e)}"

    async def _get_wallet_data(self, wallet_address: str) -> Dict[str, Any]:
        """
        Fetch wallet data including transactions and holdings.
        """
        try:
            # Get recent transactions
            transactions = await self._get_recent_transactions(wallet_address)
            
            # Get token holdings
            holdings = await self._get_token_holdings(wallet_address)
            
            # Get wallet balance
            balance = self.w3.eth.get_balance(wallet_address)
            
            return {
                "address": wallet_address,
                "balance": balance,
                "transactions": transactions,
                "holdings": holdings,
                "first_seen": self._get_first_transaction_date(transactions)
            }
        except Exception as e:
            raise Exception(f"Failed to fetch wallet data: {str(e)}")

    async def _get_recent_transactions(self, wallet_address: str) -> List[Dict[str, Any]]:
        """
        Get recent transactions for the wallet.
        """
        # This is a placeholder implementation
        # You would need to implement actual transaction fetching logic
        return []

    async def _get_token_holdings(self, wallet_address: str) -> List[Dict[str, Any]]:
        """
        Get token holdings for the wallet.
        """
        # This is a placeholder implementation
        # You would need to implement actual token holdings fetching logic
        return []

    def _analyze_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze wallet transactions for patterns and behavior.
        """
        return {
            "total_transactions": len(transactions),
            "transaction_frequency": "low",
            "average_transaction_value": 0.0,
            "suspicious_patterns": [],
            "interaction_with_known_scammers": False
        }

    def _analyze_holdings(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze wallet token holdings.
        """
        return {
            "total_tokens": len(holdings),
            "total_value": 0.0,
            "diversification_score": 0.0,
            "suspicious_tokens": []
        }

    def _check_suspicious_activity(self, wallet_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check for suspicious activity patterns.
        """
        suspicious_activities = []
        
        # Check for known scammer interaction
        if wallet_data["address"] in self.known_scammer_addresses:
            suspicious_activities.append({
                "type": "known_scammer",
                "severity": "high",
                "description": "Wallet is associated with known scammer addresses"
            })
        
        # Check for high frequency of transactions
        if wallet_data["transactions"] and len(wallet_data["transactions"]) > 100:
            suspicious_activities.append({
                "type": "high_frequency",
                "severity": "medium",
                "description": "Unusually high number of transactions"
            })
        
        return suspicious_activities

    def _get_first_transaction_date(self, transactions: List[Dict[str, Any]]) -> str:
        """
        Get the date of the first transaction.
        """
        if not transactions:
            return "Unknown"
        
        # This is a placeholder implementation
        return "Unknown"

    def _format_analysis(
        self,
        wallet_address: str,
        wallet_data: Dict[str, Any],
        transaction_analysis: Dict[str, Any],
        holdings_analysis: Dict[str, Any],
        suspicious_activity: List[Dict[str, Any]]
    ) -> str:
        """
        Format the wallet analysis results.
        """
        # Format wallet overview
        overview = f"""
👛 Wallet Analysis for {wallet_address}

💰 Overview:
• Balance: {self.w3.from_wei(wallet_data['balance'], 'ether'):.4f} ETH
• First Seen: {wallet_data['first_seen']}
• Total Tokens: {holdings_analysis['total_tokens']}
• Total Value: ${holdings_analysis['total_value']:.2f}
"""

        # Format transaction analysis
        transactions = f"""
📊 Transaction Analysis:
• Total Transactions: {transaction_analysis['total_transactions']}
• Transaction Frequency: {transaction_analysis['transaction_frequency'].title()}
• Average Transaction Value: {transaction_analysis['average_transaction_value']:.4f} ETH
• Interaction with Known Scammers: {'Yes' if transaction_analysis['interaction_with_known_scammers'] else 'No'}
"""

        # Format holdings analysis
        holdings = f"""
💎 Holdings Analysis:
• Diversification Score: {holdings_analysis['diversification_score']:.2f}/10
• Suspicious Tokens: {len(holdings_analysis['suspicious_tokens'])}
"""

        # Format suspicious activity
        if suspicious_activity:
            suspicious = "\n⚠️ Suspicious Activity Detected:\n" + "\n".join([
                f"• {activity['type'].replace('_', ' ').title()} "
                f"({activity['severity'].upper()}): {activity['description']}"
                for activity in suspicious_activity
            ])
        else:
            suspicious = "\n✅ No suspicious activity detected."

        return overview + transactions + holdings + suspicious 