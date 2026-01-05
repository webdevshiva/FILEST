from telegram import Update
from telegram.ext import ContextTypes
from db import get_session, get_force_channels, create_verification_token, validate_token, log_action, get_global_caption
from utils import shorten_url, format_time_left
from keyboards import force_join_kb, verification_kb, session_kb
from config import BOT_USERNAME, SESSION_DURATION
import time
import secrets

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    channels = await get_force_channels()
    not_joined = []
    for ch in channels:
        try:
            member = await context.bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                not_joined.append(ch)
        except:
            not_joined.append(ch)
    return len(not_joined) == 0

async def apply_caption(user_id, file_name="", batch_name=""):
    template = await get_global_caption()
    if not template:
        return None
    return template.format(
        file_name=file_name or "File",
        batch_name=batch_name or "",
        user_id=user_id,
        expiry_time=format_time_left(SESSION_DURATION)
    )

async def send_content(update: Update, context: ContextTypes.DEFAULT_TYPE, code: str):
    link = await get_link(code)
    if not link:
        await update.effective_message.reply_text("Invalid link.")
        return

    channel_id = link["channel_id"]
    caption_base = await apply_caption(update.effective_user.id, batch_name=code if link["type"] == "batch" else "")

    if link["type"] == "file":
        await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=channel_id,
            message_id=link["start_msg"],
            caption=caption_base
        )
    elif link["type"] == "batch":
        for msg_id in range(link["start_msg"], link["end_msg"] + 1):
            try:
                await context.bot.copy_message(
                    chat_id=update.effective_chat.id,
                    from_chat_id=channel_id,
                    message_id=msg_id,
                    caption=caption_base
                )
            except:
                continue  # skip unavailable messages

    await log_action(update.effective_user.id, f"accessed_{link['type']}_{code}")

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await log_action(user_id, "start")

    args = context.args
    if not args:
        await update.message.reply_text("Use admin-generated links only.")
        return

    param = args[0]

    # Verification return
    if param.startswith("verify_"):
        token = param[7:]
        doc = await validate_token(token)
        if not doc:
            await update.message.reply_text("❌ Verification Failed. Too fast or invalid!")
            return

        await create_session(user_id)
        await log_action(user_id, "verified_success")
        await update.message.reply_text("✅ Verification Successful!\nUnlimited access for 6 hours.", reply_markup=session_kb())

        code = doc.get("code")
        if code:
            await send_content(update, context, code)
        return

    code = param
    link = await get_link(code)
    if not link:
        await update.message.reply_text("Invalid or expired link.")
        return

    # Store pending code for callbacks
    context.user_data["pending_code"] = code

    session = await get_session(user_id)
    if session:
        await update.message.reply_text("🔓 Unlimited Access Active", reply_markup=session_kb())
        await send_content(update, context, code)
        return

    joined = await check_membership(update, context)
    if not joined:
        channels = await get_force_channels()
        await update.message.reply_text("🔔 Join all channels to continue", reply_markup=force_join_kb(channels))
        return

    # Verification step
    token = await create_verification_token(user_id, code)
    plain_url = f"https://t.me/{BOT_USERNAME}?start=verify_{token}"
    short_url = await shorten_url(plain_url)

    text = ("🔐 Verify & Get Unlimited Access\n\n"
            "Unlock unlimited files & batches for the next 6 hours.\n\n"
            "⚠ Open link properly and wait 35+ seconds.\n"
            "Bypass attempts are detected.")

    await update.message.reply_text(text, reply_markup=verification_kb(short_url, plain_url))