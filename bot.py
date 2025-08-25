import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_GROUP_ID = os.getenv("TARGET_GROUP_ID")
TARGET_TOPIC_ID = os.getenv("TARGET_TOPIC_ID")

if not BOT_TOKEN or not TARGET_GROUP_ID or not TARGET_TOPIC_ID:
    logging.error("❌ Missing environment variables! Please set BOT_TOKEN, TARGET_GROUP_ID, and TARGET_TOPIC_ID in Fly.io secrets.")
    raise SystemExit("Missing environment variables")

TARGET_GROUP_ID = int(TARGET_GROUP_ID)
TARGET_TOPIC_ID = int(TARGET_TOPIC_ID)

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post:
        logging.info(f"Forwarding message {update.channel_post.message_id}")
        await context.bot.forward_message(
            chat_id=TARGET_GROUP_ID,
            from_chat_id=update.channel_post.chat.id,
            message_id=update.channel_post.message_id,
            message_thread_id=TARGET_TOPIC_ID
        )

if __name__ == "__main__":
    logging.info("🚀 Starting bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL & filters.ChatType.CHANNEL, forward_message))
    app.run_polling()
 
