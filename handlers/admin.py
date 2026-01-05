from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from db import save_link, get_force_channels, add_force_channel, remove_force_channel, set_setting, get_setting, log_action
from utils import generate_code
from keyboards import admin_main_kb
from config import ADMIN_IDS

WAITING_CHANNEL, WAITING_FIRST, WAITING_LAST, WAITING_CAPTION = range(4)

async def is_admin(update: Update):
    return update.effective_user.id in ADMIN_IDS

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return
    await update.message.reply_text("Admin Panel", reply_markup=admin_main_kb())

async def link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return
    if not update.message.reply_to_message or not update.message.reply_to_message.forward_from_chat:
        await update.message.reply_text("Reply to a message forwarded from database channel.")
        return
    channel = update.message.reply_to_message.forward_from_chat.id
    msg_id = update.message.reply_to_message.forward_from_message_id
    code = generate_code("file")
    await save_link(code, "file", channel, msg_id)
    link = f"https://t.me/{context.bot.username}?start={code}"
    await update.message.reply_text(f"Single File Link:\n{link}")

async def batch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return
    await update.message.reply_text("Send first message link (forward from channel)")
    return WAITING_FIRST

async def batch_first(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # parse link or forwarded
    context.user_data["channel"] = update.message.forward_from_chat.id
    context.user_data["first"] = update.message.forward_from_message_id
    await update.message.reply_text("Send last message link")
    return WAITING_LAST

async def batch_last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel = context.user_data["channel"]
    first = context.user_data["first"]
    last = update.message.forward_from_message_id
    code = generate_code("batch")
    await save_link(code, "batch", channel, first, last)
    link = f"https://t.me/{context.bot.username}?start={code}"
    await update.message.reply_text(f"Batch Link:\n{link}")
    return ConversationHandler.END

# Add force channel management, caption set, etc. via callbacks