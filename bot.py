from discord.ext import commands
from datetime import datetime, UTC
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from keep_alive import keep_alive
import discord
import gspread
import csv
import os
import io
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

keep_alive()

# Load environment variables from .env file
load_dotenv()

# === CONFIG ===
TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # <-- Bot token from environment variable
GOOGLE_SHEET_ID = "1_-mQlKfE-jc1sw8KrAcmm57_W-BviApyj4A1lplvbDk"

if not TOKEN:
    raise ValueError("⚠️ Missing environment variable: DISCORD_BOT_TOKEN")

# === GOOGLE SHEETS SETUP ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# Load Google credentials from environment variable
google_creds_json = os.getenv("GOOGLE_CREDS_JSON")
if not google_creds_json:
    raise ValueError("⚠️ Missing environment variable: GOOGLE_CREDS_JSON")

creds_dict = json.loads(google_creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1

# === DISCORD BOT SETUP ===
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# === COMMAND: !log ===
@bot.command()
async def log(ctx, percent: float, profit: float, coin: str, direction: str):
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M")
    user = str(ctx.author)
    sheet.append_row([now, user, percent, profit, coin.upper(), direction.capitalize()])
    await ctx.send(
        f"✅ Log saved:\n"
        f"**User:** {user}\n"
        f"**Percentage:** {percent}%\n"
        f"**Profit:** ${profit}\n"
        f"**Coin:** {coin.upper()}\n"
        f"**Direction:** {direction.capitalize()}"
    )

# === COMMAND: !delete ===
@bot.command()
async def delete(ctx):
    records = sheet.get_all_values()
    if len(records) <= 1:
        await ctx.send("⚠️ No records to delete.")
        return

    user = str(ctx.author)
    for i in range(len(records)-1, 0, -1):
        if records[i][1] == user:
            try:
                sheet.delete_rows(i + 1)
                await ctx.send(f"✅ Last record for **{user}** deleted successfully.")
                return
            except Exception as e:
                await ctx.send(f"⚠️ Failed to delete the last record: {e}")
                return

    await ctx.send(f"⚠️ No records found for **{user}** to delete.")

# === COMMAND: !stats ===
@bot.command()
async def stats(ctx):
    records = sheet.get_all_values()
    if len(records) <= 1:
        await ctx.send("⚠️ No trades logged yet.")
        return

    data = records[1:]
    user = str(ctx.author)
    total_trades = 0
    net = total_perc = wins = total_profit = total_loss = 0.0
    profits = []

    for row in data:
        try:
            row_user = row[1]
            if row_user == user:
                profit = float(row[3])
                total_perc += float(row[2])
                net += profit
                total_trades += 1
                profits.append(profit)
                if profit > 0:
                    wins += 1
                    total_profit += profit
                else:
                    total_loss += profit
        except (ValueError, IndexError):
            continue

    if total_trades == 0:
        await ctx.send(f"⚠️ No trades logged yet for **{user}**.")
        return

    win_rate = (wins / total_trades * 100) if total_trades else 0.0
    profit_factor = (total_profit / total_loss * -1) if total_loss != 0 else 0.0

    # === Sortino Ratio Calculation ===
    returns = np.array(profits)
    avg_return = np.mean(returns)
    downside_returns = returns[returns < 0]
    downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
    sortino_ratio = avg_return / downside_std if downside_std != 0 else 0.0

    await ctx.send(
        f"📊 **Statistics for {user}** 📊\n"
        f"Total Trades: **{total_trades}**\n"
        f"Total Profit: **${total_profit:.2f}**\n"
        f"Total Loss: **-${total_loss * -1:.2f}**\n"
        f"Net: **${net:.2f}**\n"
        f"Percentage: **{total_perc:.2f}%**\n"
        f"Profit Factor: **{profit_factor:.2f}**\n"
        f"Sortino Ratio: **{sortino_ratio:.2f}**\n"
        f"Win Rate: **{win_rate:.2f}%**"
    )

# === COMMAND: !export ===
@bot.command()
async def export(ctx):
    records = sheet.get_all_values()
    if len(records) <= 1:
        await ctx.send("⚠️ No data to export.")
        return

    user = str(ctx.author)
    headers = records[0]
    user_records = [row for row in records[1:] if row[1] == user]

    if not user_records:
        await ctx.send(f"⚠️ No logs found for **{user}**.")
        return

    filename = f"trade_logs_{user.replace('#', '_')}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)  # write header
        writer.writerows(user_records)

    await ctx.send(f"📂 Exported {len(user_records)} logs for **{user}**:", file=discord.File(filename))
    os.remove(filename)

# === COMMAND: !equity ===
@bot.command()
async def equity(ctx):
    records = sheet.get_all_values()
    if len(records) <= 1:
        await ctx.send("⚠️ No trade data available.")
        return

    df = pd.DataFrame(records[1:], columns=records[0])
    df.columns = df.columns.str.strip().str.replace("%", "Pct").str.replace(" ", "_")
    user = str(ctx.author)
    user_df = df[df["User"] == user]

    if user_df.empty:
        await ctx.send(f"⚠️ No trades found for **{user}**.")
        return

    user_df["Date"] = pd.to_datetime(user_df["Date"], errors="coerce")
    user_df = user_df.sort_values("Date")
    user_df["Profit_Amount"] = pd.to_numeric(user_df["Profit_Amount"], errors="coerce")
    user_df["Cumulative_Profit"] = user_df["Profit_Amount"].cumsum()

    plt.figure(figsize=(10, 6))
    plt.plot(user_df["Date"], user_df["Cumulative_Profit"], color="royalblue", linewidth=2)
    plt.title(f"Equity Curve - {user}", fontsize=16)
    plt.xlabel("Date")
    plt.ylabel("Cumulative Profit ($)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    await ctx.send(file=discord.File(buf, filename="equity_curve.png"))

# === COMMAND: !note ===
@bot.command()
async def note(ctx, *, note_text: str):
    """Attach a note to the user's most recent log entry."""
    records = sheet.get_all_values()
    if len(records) <= 1:
        await ctx.send("⚠️ No records to add a note to.")
        return

    user = str(ctx.author)

    # Find the last record for this user
    for i in range(len(records) - 1, 0, -1):
        if records[i][1] == user:
            row_index = i + 1  # Google Sheets rows are 1-indexed
            existing_row = records[i]

            # Ensure 'Note' header exists
            if len(records[0]) < 7:
                sheet.update_cell(1, 7, "Note")

            # Pad row if necessary
            while len(existing_row) < 7:
                existing_row.append("")

            # Add note
            sheet.update_cell(row_index, 7, note_text)

            # Extract coin and direction from last log
            coin = existing_row[4] if len(existing_row) > 4 else "N/A"
            direction = existing_row[5] if len(existing_row) > 5 else "N/A"

            await ctx.send(f"📝 Note added to your last log: **{coin} {direction}**")
            return

    await ctx.send(f"⚠️ No previous log found for **{user}** to attach a note.")

# === RUN BOT ===
bot.run(TOKEN)