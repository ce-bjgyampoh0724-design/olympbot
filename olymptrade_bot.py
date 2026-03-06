import logging
import random
from datetime import datetime, time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, JobQueue

BOT_TOKEN = "7938417381:AAElAKZH4rW2pk39uRvo8PpbEMD18lT6vq0"
CHANNEL_ID = "@Jessebright_bot"

ASSETS = {
    "Forex": ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "EUR/GBP", "USD/CHF", "NZD/USD"],
    "Crypto": ["BTC/USD", "ETH/USD", "LTC/USD", "XRP/USD", "BNB/USD"],
    "Commodities": ["Gold (XAU/USD)", "Silver (XAG/USD)", "Crude Oil (WTI)", "Natural Gas"],
    "Indices": ["S&P 500", "NASDAQ 100", "Dow Jones", "DAX 40", "FTSE 100", "Nikkei 225"],
}

EXPIRY_OPTIONS = [1, 2, 3, 5]

SIGNAL_TIMES = [
    time(6, 0), time(8, 0), time(10, 0), time(12, 0),
    time(14, 0), time(16, 0), time(18, 0), time(20, 0),
]

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_signal():
    category = random.choice(list(ASSETS.keys()))
    asset = random.choice(ASSETS[category])
    direction = random.choice(["UP", "DOWN"])
    expiry = random.choice(EXPIRY_OPTIONS)
    confidence = random.randint(70, 92)
    now = datetime.utcnow().strftime("%H:%M UTC")
    return (
        "OLYMP TRADE SIGNAL\n"
        "----------------------------\n"
        "Asset: " + asset + " [" + category + "]\n"
        "Time: " + now + "\n"
        "Expiry: " + str(expiry) + " minute(s)\n"
        "Direction: " + direction + "\n"
        "Confidence: " + str(confidence) + "%\n"
        "----------------------------\n"
        "Trade responsibly. Past signals do not guarantee future results."
    )


def generate_batch_signals(count=4):
    seen_assets = set()
    signals = []
    attempts = 0
    while len(signals) < count and attempts < 50:
        category = random.choice(list(ASSETS.keys()))
        asset = random.choice(ASSETS[category])
        if asset in seen_assets:
            attempts += 1
            continue
        seen_assets.add(asset)
        direction = random.choice(["UP", "DOWN"])
        expiry = random.choice(EXPIRY_OPTIONS)
        confidence = random.randint(70, 92)
        signals.append({"asset": asset, "category": category, "direction": direction, "expiry": expiry, "confidence": confidence})
        attempts += 1

    now = datetime.utcnow().strftime("%H:%M UTC")
    lines = ["OLYMP TRADE SIGNALS - " + now, "=" * 30]
    for i, s in enumerate(signals, 1):
        lines.append(
            "Signal " + str(i) + " [" + s["category"] + "]\n"
            "  Asset: " + s["asset"] + "\n"
            "  Expiry: " + str(s["expiry"]) + " min\n"
            "  Direction: " + s["direction"] + "\n"
            "  Confidence: " + str(s["confidence"]) + "%"
        )
    lines.append("=" * 30)
    lines.append("Trade responsibly. For educational purposes only.")
    return "\n\n".join(lines)


async def send_scheduled_signals(context: ContextTypes.DEFAULT_TYPE):
    message = generate_batch_signals(count=4)
    await context.bot.send_message(chat_id=CHANNEL_ID, text=message)
    logger.info("Scheduled signals sent.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to OlympTrade Signal Bot!\n\n"
        "Commands:\n"
        "/signal - Get 1 signal now\n"
        "/batch  - Get 4 signals now\n"
        "/help   - Show this message\n\n"
        "Trade responsibly. This bot is for educational use only."
    )


async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_signal())


async def batch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_batch_signals(count=4))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "OlympTrade Signal Bot - Help\n\n"
        "/start  - Welcome message\n"
        "/signal - Get 1 signal instantly\n"
        "/batch  - Get 4 signals instantly\n"
        "/help   - Show this help\n\n"
        "Scheduled signals sent at:\n"
        "06:00 | 08:00 | 10:00 | 12:00\n"
        "14:00 | 16:00 | 18:00 | 20:00 UTC\n\n"
        "Signals are educational only. Always manage your risk."
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal_command))
    app.add_handler(CommandHandler("batch", batch_command))
    app.add_handler(CommandHandler("help", help_command))
    job_queue = app.job_queue
    for t in SIGNAL_TIMES:
        job_queue.run_daily(send_scheduled_signals, time=t)
    logger.info("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()