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