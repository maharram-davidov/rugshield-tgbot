# Memecoin Analyzer Telegram Bot

A comprehensive Telegram bot for analyzing memecoins, tracking social media sentiment, analyzing wallet behavior, reviewing smart contracts, and detecting potential scams.

## Features

- 🤖 AI-powered token analysis using Google's Gemini AI
- 📊 Social media sentiment tracking
- 👛 Wallet behavior analysis
- 🔍 Smart contract review
- ⚠️ Scam detection and database
- 💡 Real-time alerts and recommendations

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/memecoin-analyzer-bot.git
cd memecoin-analyzer-bot
```

2. Create a virtual environment and activate it:
```bash
# On Windows:
python -m venv .venv
.venv\Scripts\activate

# On Linux/Mac:
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
# On Windows:
python setup.py

# On Linux/Mac:
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys and configuration:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ETHEREUM_RPC_URL=your_ethereum_rpc_url
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
GEMINI_API_KEY=your_gemini_api_key
```

5. Run the bot:
```bash
python bot.py
```

## Usage

The bot supports the following commands:

- `/start` - Display welcome message and available commands
- `/analyze <token_address>` - Analyze a specific token
- `/sentiment <token_symbol>` - Check social media sentiment
- `/contract <token_address>` - Review smart contract
- `/wallet <address>` - Analyze wallet behavior
- `/scam_check <token_address>` - Check scam database

## Features in Detail

### AI Analysis (Gemini AI)
- Advanced market trend analysis
- Price movement prediction
- Volume analysis
- Holder distribution analysis
- Liquidity assessment
- Natural language insights

### Social Media Sentiment
- Twitter sentiment tracking
- Reddit community analysis
- Telegram channel monitoring
- Overall sentiment scoring
- AI-powered sentiment insights

### Wallet Analysis
- Transaction history analysis
- Token holding patterns
- Interaction with known addresses
- Suspicious activity detection

### Smart Contract Review
- Contract code analysis
- Security vulnerability detection
- Scam pattern recognition
- Best practice compliance check
- AI-powered security insights

### Scam Detection
- Known scam database
- Suspicious pattern recognition
- Real-time scam alerts
- Community-reported scams

## Troubleshooting

If you encounter any issues during installation:

1. Make sure you have Python 3.8 or higher installed
2. On Windows, ensure you have the latest version of pip:
```bash
python -m pip install --upgrade pip
```
3. If you encounter build errors, try installing the Visual C++ build tools:
   - Download and install from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - During installation, select "Desktop development with C++"

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This bot is for informational purposes only. Always do your own research (DYOR) before making any investment decisions. The bot's analysis should not be considered as financial advice. 