# Discord Trading Logger Bot

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
