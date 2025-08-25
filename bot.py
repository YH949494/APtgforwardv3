import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_GROUP_ID = os.getenv("TARGET_GROUP_ID")
TARGET_TOPIC_ID = os.getenv("TARGET_TOPIC_ID")

if not BOT_TOKEN or not TARGET_GROUP_ID or not TARGET_TOPIC_ID:
    logging.error("❌ Missing environment variables! Please set BOT_TOKEN, TARGET_GROUP_ID, and TARGET_TOPIC_ID in Fly.io secrets.")
    raise SystemExit("Missing environment variables")

TARGET_GROUP_ID = int(TARGET_GROUP_ID)
TARGET_TOPIC_ID = int(TARGET_TOPIC_ID)

# Forwarding function
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post:
        logging.info(f"Forwarding message {update.channel_post.message_id}")
        await context.bot.forward_message(
            chat_id=TARGET_GROUP_ID,
            from_chat_id=update.channel_post.chat.id,
            message_id=update.channel_post.message_id,
            message_thread_id=TARGET_TOPIC_ID
        )

# Main async loop with 5-minute polling
async def main():
    logging.info("🚀 Starting bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL & filters.ChatType.CHANNEL, forward_message))

    while True:
        logging.info("Polling for new messages...")
        await app.update_queue.start_polling()
        logging.info("Sleeping for 5 minutes before next poll...")
        await asyncio.sleep(300)  # 300 seconds = 5 minutes

if __name__ == "__main__":
    asyncio.run(main())
