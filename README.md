# Discord Trade Logger Bot

![Banner](https://i.imgur.com/JT8oblS.png)

A Discord bot to log trades, track statistics, visualize equity curves, and export trading data using Google Sheets. Configurable via environment variables for secure deployment locally or on cloud platforms.

## Features

- `!log` — Log a new trade with percentage, profit, coin, and direction.  
- `!delete` — Delete the last trade entry for a user.  
- `!stats` — View trade statistics including net profit, win rate, and profit factor.  
- `!export` — Export all trade logs as a CSV file.  
- `!equity` — Generate a cumulative profit graph (equity curve) for a user.  
- Supports multiple users with separate logs.  
- Uses Google Sheets for storage.  
- Fully environment-variable driven for secure credentials management.

### Setup bot with following url
- [Setup link](https://discord.com/oauth2/authorize?client_id=1423380213827371048&permissions=68608&integration_type=0&scope=bot)

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/guvenk/TradeLogger.git
cd TradeLogger
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create a .env file
Create a .env file in the project root:

```env
# Discord bot token
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# Google service account credentials
GOOGLE_CREDS_JSON='{
  "type": "service_account",
  "project_id": "api-project-XXXXX",
  "private_key_id": "XXXXX",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account-email@project.iam.gserviceaccount.com",
  "client_id": "XXXXX",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account-email@project.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}'
```

### 4. Google Sheets Setup

Create a Google Sheet to store trade logs.

Share the sheet with the service account email from your credentials.

Copy the Google Sheet ID and update the GOOGLE_SHEET_ID variable in your script.

### 5. Run the Bot
```bash
python bot.py
```

The bot will read credentials from the .env file when running locally, or from environment variables on cloud platforms.


## License

This project is licensed under the [MIT License](LICENSE).