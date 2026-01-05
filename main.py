import os
import logging
import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from config import BOT_TOKEN
from db import init_db
from handlers.start import start_handler
from handlers.callback import callback_handler
from handlers.admin import (
    admin_handler,
    link_command,
    batch_command,
    batch_first,
    batch_last,
)

logging.basicConfig(level=logging.INFO)

WAITING_FIRST, WAITING_LAST = range(2)

async def main():
    init_db()  # MongoDB connection & indexes

    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("admin", admin_handler))
    app.add_handler(CommandHandler("link", link_command))

    # Batch conversation
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("batch", batch_command)],
        states={
            WAITING_FIRST: [MessageHandler(filters.FORWARDED, batch_first)],
            WAITING_LAST: [MessageHandler(filters.FORWARDED, batch_last)],
        },
        fallbacks=[],
    ))

    # Callbacks
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Webhook setup for Render.com
    port = int(os.environ.get("PORT", 10000))
    webhook_url = os.getenv("WEBHOOK_URL", f"https://{os.getenv('RENDER_SERVICE_NAME')}.onrender.com/")

    await app.initialize()
    await app.start()
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=BOT_TOKEN,
        webhook_url=webhook_url + BOT_TOKEN,
    )
    logging.info("Bot started with webhook")
    await asyncio.Event().wait()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())