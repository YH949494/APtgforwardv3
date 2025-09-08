import os
import logging
import asyncio
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

# ----------------------
# Config
# ----------------------

# Force httpx to use IPv4
os.environ["HTTPX_LOCAL_ADDRESS"] = "0.0.0.0"

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_GROUP_ID = int(os.getenv("TARGET_GROUP_ID"))
SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID"))
FLY_APP_NAME = os.getenv("FLY_APP_NAME")
PORT = int(os.getenv("PORT", 8080))

if not BOT_TOKEN or not TARGET_GROUP_ID or not SOURCE_CHANNEL_ID or not FLY_APP_NAME:
    logging.error("❌ Missing environment variables! Please set BOT_TOKEN, TARGET_GROUP_ID, SOURCE_CHANNEL_ID, and FLY_APP_NAME in Fly.io secrets.")
    raise SystemExit("Missing environment variables")

WEBHOOK_URL = f"https://{FLY_APP_NAME}.fly.dev/webhook"

# ----------------------
# Handlers
# ----------------------

async def copy_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Copy messages from the source channel to the target group."""
    if update.channel_post and update.channel_post.chat.id == SOURCE_CHANNEL_ID:
        logging.info(f"📩 Copying message {update.channel_post.message_id} from channel {SOURCE_CHANNEL_ID}")
        try:
            await context.bot.copy_message(
                chat_id=TARGET_GROUP_ID,
                from_chat_id=update.channel_post.chat.id,
                message_id=update.channel_post.message_id,
            )
            logging.info("✅ Copy success")
        except Exception as e:
            logging.error(f"❌ Failed to copy message: {e}")

async def debug_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log all incoming updates."""
    logging.info(f"📥 Incoming update: {update.to_dict()}")

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test command to check if bot and webhook are alive."""
    try:
        await update.message.reply_text("🏓 Pong! Bot is alive and webhook is working.")
        logging.info("✅ Replied to /ping")
    except Exception as e:
        logging.error(f"❌ Failed to reply to /ping: {e}")

# ----------------------
# Main
# ----------------------

if __name__ == "__main__":
    logging.info("🚀 Starting bot in webhook mode...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, copy_message_handler))
    app.add_handler(MessageHandler(filters.ALL, debug_handler))
    app.add_handler(CommandHandler("ping", ping_command))

    # Setup webhook
    async def setup_webhook():
        bot = Bot(BOT_TOKEN)
        # Remove any old webhook and pending updates
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"✅ Webhook set to {WEBHOOK_URL}")

    asyncio.get_event_loop().run_until_complete(setup_webhook())

    # Run webhook server
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=WEBHOOK_URL,
        drop_pending_updates=True,
    )
