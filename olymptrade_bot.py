import logging
import random
from datetime import datetime, time, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, JobQueue

BOT_TOKEN = "7938417381:AAElAKZH4rW2pk39uRvo8PpbEMD18lT6vq0"
CHANNEL_ID = "@Jessebright_bot"

ASSETS = {
    "Forex OTC": [
        "AUD/CAD OTC", "AUD/CHF OTC", "AUD/JPY OTC", "AUD/NZD OTC", "AUD/USD OTC",
        "CAD/CHF OTC", "CAD/JPY OTC", "CHF/JPY OTC",
        "EUR/AUD OTC", "EUR/CAD OTC", "EUR/CHF OTC", "EUR/GBP OTC",
        "EUR/JPY OTC", "EUR/USD OTC",
        "GBP/AUD OTC", "GBP/CAD OTC", "GBP/CHF OTC", "GBP/JPY OTC",
        "GBP/NZD OTC", "GBP/USD OTC",
        "NZD/CAD OTC", "NZD/CHF OTC", "NZD/JPY OTC",
    ],
    "Crypto OTC": [
        "Bitcoin OTC", "Ethereum OTC", "Dogecoin OTC",
    ],
    "Commodities OTC": [
        "Gold OTC", "BRENT OTC",
    ],
    "Indices OTC": [
        "Asia Composite Index", "Europe Composite Index", "Arabia General Index",
        "Basic Altcoin Index", "Crypto Composite Index", "Compound Index",
        "Halal Market Axis", "Quickler",
    ],
}

EXPIRY_OPTIONS = [1, 2, 3, 5]

SIGNAL_TIMES = [
    time(6, 0),
    time(8, 0),
    time(10, 0),
    time(12, 0),
    time(14, 0),
    time(16, 0),
    time(18, 0),
    time(20, 0),
]

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_signal():
    category = random.choice(list(ASSETS.keys()))
    asset = random.choice(ASSETS[category])
    direction = random.choice(["BUY", "SELL"])
    expiry = random.choice(EXPIRY_OPTIONS)
    confidence = random.randint(70, 92)
    now = datetime.utcnow()
    entry_time = now + timedelta(minutes=1)
    level1 = entry_time + timedelta(minutes=expiry)
    level2 = level1 + timedelta(minutes=expiry)
    level3 = level2 + timedelta(minutes=expiry)
    signal = (
        "NEW SIGNAL!\n\n"
        "Trade: " + asset + "\n"
        "Timer: " + str(expiry) + " minutes\n"
        "Entry: " + entry_time.strftime("%I:%M %p") + "\n"
        "Direction: " + direction + "\n"
        "Confidence: " + str(confidence) + "%\n\n"
        "Martingale Levels:\n"
        "Level 1 -> " + level1.strftime("%I:%M %p") + "\n"
        "Level 2 -> " + level2.strftime("%I:%M %p") + "\n"
        "Level 3 -> " + level3.strftime("%I:%M %p") + "\n\n"
        "Trade responsibly. For educational purposes only."
    )
    return signal


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
        direction = random.choice(["BUY", "SELL"])
        expiry = random.choice(EXPIRY_OPTIONS)
        confidence = random.randint(70, 92)
        signals.append({
            "asset": asset,
            "category": category,
            "direction": direction,
            "expiry": expiry,
            "confidence": confidence,
        })
        attempts += 1

    now = datetime.utcnow()
    header_time = now.strftime("%I:%M %p UTC")
    lines = ["OLYMP TRADE SIGNALS - " + header_time, "=" * 32]

    for i, s in enumerate(signals, 1):
        entry_time = now + timedelta(minutes=i)
        level1 = entry_time + timedelta(minutes=s["expiry"])
        level2 = level1 + timedelta(minutes=s["expiry"])
        level3 = level2 + timedelta(minutes=s["expiry"])
        lines.append(
            "Signal " + str(i) + "\n"
            "Trade: " + s["asset"] + "\n"
            "Timer: " + str(s["expiry"]) + " minutes\n"
            "Entry: " + entry_time.strftime("%I:%M %p") + "\n"
            "Direction: " + s["direction"] + "\n"
            "Confidence: " + str(s["confidence"]) + "%\n"
            "Martingale Levels:\n"
            "  Level 1 -> " + level1.strftime("%I:%M %p") + "\n"
            "  Level 2 -> " + level2.strftime("%I:%M %p") + "\n"
            "  Level 3 -> " + level3.strftime("%I:%M %p")
        )
        lines.append("-" * 32)

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
