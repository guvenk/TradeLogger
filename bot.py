import discord
from discord.ext import commands
from datetime import datetime, UTC
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
import os

from keep_alive import keep_alive
keep_alive()

# === CONFIG ===
TOKEN = "MTQyMzM4MDIxMzgyNzM3MTA0OA.Gawy1B.XhNzzqN-NuArU_-ArO-ofw32Qo6VaVt_SRir04" # Discord Bot Token
GOOGLE_SHEET_ID = "1_-mQlKfE-jc1sw8KrAcmm57_W-BviApyj4A1lplvbDk"
CHANNEL_ID = 1423319542310109244

# === GOOGLE SHEETS SETUP ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1


# === DISCORD BOT SETUP ===
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


# Restrict all commands to a single channel
@bot.check
async def restrict_to_channel(ctx):
    return ctx.channel.id == CHANNEL_ID


# === Global Error Handler ===
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(f"⚠️ Commands are only allowed in the designated channel.")


# === COMMAND: !log ===
@bot.command()
async def log(ctx, percent: float, profit: float, coin: str, direction: str):
    """
    Example usage:
    !log 1.2 120 BTC long
    """
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    user = str(ctx.author)

    # Save to Google Sheets
    sheet.append_row([now, user, percent, profit, coin.upper(), direction.capitalize()])

    # Confirmation
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send(
        f"✅ Log saved:\n"
        f"**User:** {user}\n"
        f"**Percentage:** {percent}%\n"
        f"**Profit:** ${profit}\n"
        f"**Coin:** {coin.upper()}\n"
        f"**Direction:** {direction.capitalize()}"
    )


# === COMMAND: !stats ===
@bot.command()
async def stats(ctx):
    """
    Shows total profit, win rate, and number of trades for the user
    """
    records = sheet.get_all_values()

    if len(records) <= 1:
        await channel.send("⚠️ No trades logged yet.")
        return

    # Skip header row
    data = records[1:]  

    user = str(ctx.author)  # Discord username#discriminator
    total_trades = 0
    total_profit = 0.0
    total_perc = 0.0
    wins = 0

    for row in data:
        try:
            row_user = row[1]  # "User" column (second column in log)
            if row_user == user:
                profit = float(row[3])  # Profit Amount column
                total_perc += float(row[2]) # Profit % column
                total_profit += profit
                total_trades += 1
                if profit > 0:
                    wins += 1
        except (ValueError, IndexError):
            continue

    if total_trades == 0:
        await channel.send(f"⚠️ No trades logged yet for **{user}**.")
        return

    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0

    await channel.send(
        f"📊 **Statistics for {user}** 📊\n"
        f"Total Trades: **{total_trades}**\n"
        f"Profit: **${total_profit:.2f}**\n"
        f"Percentage: **{total_perc:.2f}%**\n"
        f"Win Rate: **{win_rate:.2f}%**"
    )


# === COMMAND: !export ===
@bot.command()
async def export(ctx):
    records = sheet.get_all_values()
    if len(records) == 0:
        await channel.send("⚠️ No data to export.")
        return

    # Save as CSV
    filename = "trade_logs.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(records)

    # Send file to Discord
    await channel.send(f"📂 {len(records)} logs:", file=discord.File(filename))

    # Print to console
    print(f"[EXPORT] Exported {len(records)} rows to {filename}")

    # Clean up file (optional)
    os.remove(filename)


# === RUN BOT ===
bot.run(TOKEN)