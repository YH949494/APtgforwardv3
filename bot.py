import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# Force httpx to IPv4
os.environ["HTTPX_LOCAL_ADDRESS"] = "0.0.0.0"

logging.basicConfig(level=logging.INFO)

# Env vars
BOT_TOKEN = os.getenv("BOT_TOKEN")  
TARGET_GROUP_ID = int(os.getenv("TARGET_GROUP_ID"))
SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID"))
FLY_APP_NAME = os.getenv("FLY_APP_NAME")
PORT = int(os.getenv("PORT", 8080))

# Copy function
async def copy_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.chat.id == SOURCE_CHANNEL_ID:
        logging.info(f"📩 Copying message {update.channel_post.message_id}")
        try:
            await context.bot.copy_message(
                chat_id=TARGET_GROUP_ID,
                from_chat_id=update.channel_post.chat.id,
                message_id=update.channel_post.message_id
            )
        except Exception as e:
            logging.error(f"❌ Failed to copy message: {e}")

# Debug
async def debug_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"📥 Incoming update: {update.to_dict()}")

# /ping
async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Bot is alive and webhook is working.")

if __name__ == "__main__":
    logging.info("🚀 Starting bot in webhook mode...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, copy_message_handler))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(MessageHandler(filters.ALL, debug_handler))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=f"https://{FLY_APP_NAME}.fly.dev/webhook",
        drop_pending_updates=True,   # 👈 add this
    )
