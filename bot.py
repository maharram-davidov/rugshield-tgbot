import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from dotenv import load_dotenv
from modules.analyzer import TokenAnalyzer
from modules.sentiment import SentimentAnalyzer
from modules.contract import ContractAnalyzer
from modules.wallet import WalletAnalyzer
from modules.scam_database import ScamDatabase
from modules.gemini_ai import GeminiAI
from modules.social_analyzer import SocialAnalyzer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MemecoinAnalyzerBot:
    def __init__(self):
        self.token_analyzer = TokenAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.contract_analyzer = ContractAnalyzer()
        self.wallet_analyzer = WalletAnalyzer()
        self.scam_database = ScamDatabase()
        self.gemini_ai = GeminiAI()
        self.social_analyzer = SocialAnalyzer()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        keyboard = [
            [
                InlineKeyboardButton("🔍 Analyze Token", callback_data="analyze"),
                InlineKeyboardButton("📊 View Metrics", callback_data="metrics")
            ],
            [
                InlineKeyboardButton("⚠️ Check Risk", callback_data="risk"),
                InlineKeyboardButton("📱 Social Analysis", callback_data="social")
            ],
            [
                InlineKeyboardButton("📝 Contract Analysis", callback_data="contract"),
                InlineKeyboardButton("❓ Help", callback_data="help")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        welcome_message = """
🚀 *Welcome to RugShield Bot!*

I'm your AI-powered token analyzer and scam detector. Here's what I can do:

*Quick Actions:*
• 🔍 Analyze any token
• 📊 View detailed metrics
• ⚠️ Check risk levels
• 📱 Analyze social presence
• 📝 Review smart contracts

*How to use:*
1. Send a token address or use the buttons below
2. I'll analyze the token comprehensively
3. Get detailed reports and risk assessments

*Example:*
`/analyze 0x123...abc`

_Select an option below to get started!_
        """
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks."""
        query = update.callback_query
        await query.answer()

        if query.data == "help":
            help_message = """
*📚 How to Use RugShield Bot*

*Commands:*
• `/analyze <address>` - Full token analysis
• `/metrics <address>` - Detailed metrics
• `/risk <address>` - Risk assessment
• `/social <address>` - Social media analysis
• `/contract <address>` - Smart contract review

*Tips:*
• Always verify token addresses
• Check multiple metrics
• Read risk assessments carefully
• Use social analysis for community insights

*Need help?* Contact @support
            """
            await query.edit_message_text(help_message, parse_mode='Markdown')
            return

        await query.edit_message_text("Please enter the token address:", parse_mode='Markdown')
        context.user_data['pending_action'] = query.data

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user messages."""
        if 'pending_action' not in context.user_data:
            await update.message.reply_text("Please use /start to begin or select an option.")
            return

        token_address = update.message.text.strip()
        action = context.user_data['pending_action']
        del context.user_data['pending_action']

        if action == "analyze":
            await self.analyze_token(update, context)
        elif action == "metrics":
            await self.analyze_metrics(update, context)
        elif action == "risk":
            await self.analyze_risk(update, context)
        elif action == "social":
            await self.analyze_social(update, context)
        elif action == "contract":
            await self.analyze_contract(update, context)

    async def analyze_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Analyze a token using AI."""
        try:
            token_address = context.args[0] if context.args else None
            if not token_address:
                await update.message.reply_text("Please provide a token address.\nExample: /analyze 0x123...abc")
                return

            message = await update.message.reply_text("🔍 *Analyzing token...*\n_This may take a few moments._", parse_mode='Markdown')

            token_data = await self.token_analyzer.analyze(token_address)
            gemini_analysis = await self.gemini_ai.analyze_token(token_data)

            # Create keyboard for additional actions
            keyboard = [
                [
                    InlineKeyboardButton("📊 View Metrics", callback_data=f"metrics_{token_address}"),
                    InlineKeyboardButton("⚠️ Check Risk", callback_data=f"risk_{token_address}")
                ],
                [
                    InlineKeyboardButton("📱 Social Analysis", callback_data=f"social_{token_address}"),
                    InlineKeyboardButton("📝 Contract Analysis", callback_data=f"contract_{token_address}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Format the response with proper escaping
            response = f"""
🔍 *Token Analysis for {self._escape_markdown(token_address)}*

💰 *Price:* `${token_data['price']:,.8f}`
📊 *Market Cap:* `${token_data['market_cap']:,.2f}`
📈 *24h Volume:* `${token_data['volume_24h']:,.2f}`
👥 *Holders:* `{token_data['holders']:,}`

🤖 *AI Analysis:*
{self._format_ai_analysis(gemini_analysis)}

_Select an option below for more details_
            """
            await message.edit_text(response, reply_markup=reply_markup, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error in analyze_token: {str(e)}")
            await update.message.reply_text(f"❌ *Error analyzing token:* `{str(e)}`", parse_mode='Markdown')

    def _escape_markdown(self, text: str) -> str:
        """Escape special characters for Markdown formatting."""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text

    def _format_ai_analysis(self, analysis: str) -> str:
        """Format AI analysis text to be Markdown-safe."""
        # Split the analysis into lines
        lines = analysis.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                formatted_lines.append('')
                continue
                
            # Check if line starts with a bullet point or number
            if line.strip().startswith(('•', '-', '*', '1.', '2.', '3.', '4.', '5.')):
                # Escape special characters in the line
                formatted_line = self._escape_markdown(line)
                formatted_lines.append(formatted_line)
            else:
                # For regular text, escape special characters
                formatted_line = self._escape_markdown(line)
                formatted_lines.append(formatted_line)
        
        return '\n'.join(formatted_lines)

    async def analyze_metrics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get detailed token metrics."""
        try:
            token_address = context.args[0] if context.args else None
            if not token_address:
                await update.message.reply_text("Please provide a token address.\nExample: /metrics 0x123...abc")
                return

            message = await update.message.reply_text("📊 *Fetching metrics...*", parse_mode='Markdown')

            token_data = await self.token_analyzer.analyze(token_address)
            metrics = token_data['metrics']

            response = f"""
📊 *Detailed Metrics for {self._escape_markdown(token_address)}*

*Market Analysis:*
• Price Trend: `{self._escape_markdown(metrics['price_trend'].title())}`
• Volume Analysis: `{self._escape_markdown(metrics['volume_analysis'].title())}`
• Holder Distribution: `{self._escape_markdown(metrics['holder_distribution'].title())}`
• Liquidity Analysis: `{self._escape_markdown(metrics['liquidity_analysis'].title())}`

*Raw Metrics:*
• Price: `${metrics['raw_metrics'].get('price', 0):,.8f}`
• Market Cap: `${metrics['raw_metrics'].get('market_cap', 0):,.2f}`
• 24h Volume: `${metrics['raw_metrics'].get('volume_24h', 0):,.2f}`
• Holders: `{metrics['raw_metrics'].get('holders', 0):,}`
            """
            await message.edit_text(response, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error in analyze_metrics: {str(e)}")
            await update.message.reply_text(f"❌ *Error fetching metrics:* `{str(e)}`", parse_mode='Markdown')

    async def analyze_risk(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Analyze token risk level."""
        try:
            token_address = context.args[0] if context.args else None
            if not token_address:
                await update.message.reply_text("Please provide a token address.\nExample: /risk 0x123...abc")
                return

            message = await update.message.reply_text("⚠️ *Analyzing risk...*", parse_mode='Markdown')

            token_data = await self.token_analyzer.analyze(token_address)
            risk = token_data['risk_assessment']

            # Create risk level emoji
            risk_emoji = {
                "extreme": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
                "minimal": "🟢"
            }.get(risk['overall_risk'], "⚪")

            response = f"""
⚠️ *Risk Analysis for {self._escape_markdown(token_address)}*

{risk_emoji} *Overall Risk:* `{self._escape_markdown(risk['overall_risk'].upper())}`

*Risk Factors:*
{chr(10).join(f'• {self._escape_markdown(factor)}' for factor in risk['risk_factors'])}

*Recommendations:*
{chr(10).join(f'• {self._escape_markdown(rec)}' for rec in risk['recommendations'])}

*Risk Metrics:*
• Market Cap Risk: {'✅' if not risk['risk_metrics'].get('market_cap_risk') else '❌'}
• Volume Risk: {'✅' if not risk['risk_metrics'].get('volume_risk') else '❌'}
• Holder Risk: {'✅' if not risk['risk_metrics'].get('holder_risk') else '❌'}
• Liquidity Risk: {'✅' if not risk['risk_metrics'].get('liquidity_risk') else '❌'}
            """
            await message.edit_text(response, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error in analyze_risk: {str(e)}")
            await update.message.reply_text(f"❌ *Error analyzing risk:* `{str(e)}`", parse_mode='Markdown')

    async def analyze_social(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Analyze social media presence."""
        try:
            token_address = context.args[0] if context.args else None
            if not token_address:
                await update.message.reply_text("Please provide a token address.\nExample: /social 0x123...abc")
                return

            message = await update.message.reply_text("📱 *Analyzing social media...*", parse_mode='Markdown')

            # Get token data first
            token_data = await self.token_analyzer.analyze(token_address)
            if not token_data:
                await message.edit_text("❌ *Error:* Could not fetch token data. Please check the address and try again.", parse_mode='Markdown')
                return

            # Get token symbol and name
            token_symbol = token_data.get('symbol', '')
            token_name = token_data.get('name', '')
            
            if not token_symbol:
                await message.edit_text("❌ *Error:* Could not determine token symbol. Please try again later.", parse_mode='Markdown')
                return

            # Get social media data
            social_data = await self.social_analyzer.analyze(token_address, token_symbol)
            if not social_data:
                await message.edit_text("❌ *Error:* Could not fetch social media data. Please try again later.", parse_mode='Markdown')
                return

            # Get AI analysis
            gemini_analysis = await self.gemini_ai.analyze_sentiment(social_data)

            # Get activity level emoji
            activity_emoji = {
                "very_high": "🟢",
                "high": "🟡",
                "medium": "🟠",
                "low": "🔴",
                "very_low": "⚫"
            }.get(social_data['activity_level'], "⚪")

            # Format the response
            response = f"""
📱 *Social Media Analysis for {self._escape_markdown(token_name)} ({self._escape_markdown(token_symbol)})*

*Twitter Stats:*
• Mentions: `{social_data['twitter_mentions']:,}`
• Engagement: `{social_data['platform_data']['twitter']['engagement']:,}`
• Sentiment Score: `{social_data['sentiment_score']:.2f}`
• Activity Level: {activity_emoji} `{social_data['activity_level'].replace('_', ' ').title()}`

*AI Analysis:*
{self._format_ai_analysis(gemini_analysis)}

*Recent Activity:*
{self._format_recent_tweets(social_data['platform_data']['twitter']['recent_tweets'])}
            """
            await message.edit_text(response, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error in analyze_social: {str(e)}")
            error_message = f"❌ *Error analyzing social media:* `{self._escape_markdown(str(e))}`"
            if isinstance(message, str):
                await update.message.reply_text(error_message, parse_mode='Markdown')
            else:
                await message.edit_text(error_message, parse_mode='Markdown')

    def _format_recent_tweets(self, tweets: list) -> str:
        """Format recent tweets for display."""
        if not tweets:
            return "_No recent tweets found_"

        formatted_tweets = []
        for tweet in tweets:
            # Format tweet text
            text = tweet.get('text', '')[:100] + '...' if len(tweet.get('text', '')) > 100 else tweet.get('text', '')
            
            # Get engagement metrics
            metrics = tweet.get('public_metrics', {})
            likes = metrics.get('like_count', 0)
            retweets = metrics.get('retweet_count', 0)
            replies = metrics.get('reply_count', 0)
            
            # Get author info
            author = tweet.get('author', {})
            username = author.get('username', '')
            followers = author.get('followers', 0)
            
            # Format the tweet
            formatted_tweet = f"""
• @{self._escape_markdown(username)} ({followers:,} followers)
  {self._escape_markdown(text)}
  ❤️ {likes:,} | 🔄 {retweets:,} | 💬 {replies:,}"""
            formatted_tweets.append(formatted_tweet)

        return '\n'.join(formatted_tweets)

    async def analyze_contract(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Analyze smart contract."""
        try:
            token_address = context.args[0] if context.args else None
            if not token_address:
                await update.message.reply_text("Please provide a token address.\nExample: /contract 0x123...abc")
                return

            message = await update.message.reply_text("📝 *Analyzing contract...*", parse_mode='Markdown')

            contract_data = await self.contract_analyzer.analyze(token_address)
            gemini_analysis = await self.gemini_ai.analyze_contract(contract_data)

            response = f"""
📝 *Contract Analysis for {self._escape_markdown(token_address)}*

*Contract Type:* `{self._escape_markdown(contract_data['type'])}`

*Features:*
{chr(10).join(f'✅ {self._escape_markdown(feature)}' for feature in contract_data['features'])}

*Known Issues:*
{chr(10).join(f'⚠️ {self._escape_markdown(issue)}' for issue in contract_data['known_issues'])}

*AI Analysis:*
{self._format_ai_analysis(gemini_analysis)}
            """
            await message.edit_text(response, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error in analyze_contract: {str(e)}")
            await update.message.reply_text(f"❌ *Error analyzing contract:* `{str(e)}`", parse_mode='Markdown')

    def _get_platform_status(self, platform_data: dict) -> str:
        """Get platform status with emoji."""
        if platform_data.get('mentions', 0) > 1000 or platform_data.get('posts', 0) > 1000 or platform_data.get('messages', 0) > 1000:
            return "🟢 Active"
        elif platform_data.get('mentions', 0) > 100 or platform_data.get('posts', 0) > 100 or platform_data.get('messages', 0) > 100:
            return "🟡 Moderate"
        else:
            return "🔴 Low Activity"

    async def analyze_wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Analyze wallet behavior."""
        if not context.args:
            await update.message.reply_text("Please provide a wallet address to analyze.")
            return

        wallet_address = context.args[0]
        await update.message.reply_text("🔍 Analyzing wallet behavior...")

        try:
            analysis = await self.wallet_analyzer.analyze(wallet_address)
            await update.message.reply_text(f"👛 Wallet Analysis:\n\n{analysis}")
        except Exception as e:
            logger.error(f"Error analyzing wallet: {str(e)}")
            await update.message.reply_text("❌ Error analyzing wallet. Please try again later.")

    async def check_scam(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check if a token is in the scam database."""
        if not context.args:
            await update.message.reply_text("Please provide a token address to check.")
            return

        token_address = context.args[0]
        await update.message.reply_text("🔍 Checking scam database...")

        try:
            result = await self.scam_database.check_token(token_address)
            await update.message.reply_text(f"⚠️ Scam Check Results:\n\n{result}")
        except Exception as e:
            logger.error(f"Error checking scam database: {str(e)}")
            await update.message.reply_text("❌ Error checking scam database. Please try again later.")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Create bot instance
    bot = MemecoinAnalyzerBot()

    # Add handlers
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("analyze", bot.analyze_token))
    application.add_handler(CommandHandler("metrics", bot.analyze_metrics))
    application.add_handler(CommandHandler("risk", bot.analyze_risk))
    application.add_handler(CommandHandler("social", bot.analyze_social))
    application.add_handler(CommandHandler("contract", bot.analyze_contract))
    application.add_handler(CommandHandler("wallet", bot.analyze_wallet))
    application.add_handler(CommandHandler("scam_check", bot.check_scam))
    application.add_handler(CallbackQueryHandler(bot.button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 