import os
import logging

# ✅ Force httpx (used by python-telegram-bot) to use IPv4 only
os.environ["HTTPX_LOCAL_ADDRESS"] = "0.0.0.0"

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters 

logging.basicConfig(level=logging.INFO)

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN") 
TARGET_GROUP_ID = os.getenv("TARGET_GROUP_ID")
SOURCE_CHANNEL_ID = os.getenv("SOURCE_CHANNEL_ID")
FLY_APP_NAME = os.getenv("FLY_APP_NAME")  # 👈 Fly app name for webhook URL
PORT = int(os.getenv("PORT", 8080))       # default port Fly uses

if not BOT_TOKEN or not TARGET_GROUP_ID or not SOURCE_CHANNEL_ID or not FLY_APP_NAME:
    logging.error("❌ Missing environment variables! Please set BOT_TOKEN, TARGET_GROUP_ID, SOURCE_CHANNEL_ID, and FLY_APP_NAME in Fly.io secrets.")
    raise SystemExit("Missing environment variables")

TARGET_GROUP_ID = int(TARGET_GROUP_ID)
SOURCE_CHANNEL_ID = int(SOURCE_CHANNEL_ID)

# ✅ Copying function
async def copy_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.chat.id == SOURCE_CHANNEL_ID:
        logging.info(f"📩 Copying message {update.channel_post.message_id} from channel {SOURCE_CHANNEL_ID}")
        try:
            await context.bot.copy_message(
                chat_id=TARGET_GROUP_ID,
                from_chat_id=update.channel_post.chat.id,
                message_id=update.channel_post.message_id
            )
            logging.info("✅ Copy success")
        except Exception as e:
            logging.error(f"❌ Failed to copy message: {e}")

if __name__ == "__main__":
    logging.info("🚀 Starting bot in webhook mode...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(MessageHandler(filters.ALL & filters.ChatType.CHANNEL, copy_message_handler))

    # Webhook URL (must be HTTPS + unique for your bot)
    WEBHOOK_URL = f"https://{FLY_APP_NAME}.fly.dev/webhook"

    # Start webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
        secret_token=None,  # optional: set if you want extra security
    )
