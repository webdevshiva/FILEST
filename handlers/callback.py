from telegram import Update
from telegram.ext import ContextTypes
from db import get_session, get_force_channels, create_verification_token
from utils import shorten_url, format_time_left
from keyboards import force_join_kb, verification_kb, session_kb
from handlers.start import check_membership, send_content
from config import BOT_USERNAME

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "recheck_force":
        joined = await check_membership(update, context)
        if joined:
            await query.edit_message_text("✅ All channels joined. Starting verification...")
            # Trigger verification (reuse code from start)
            code = context.user_data.get("pending_code")  # store in user_data during flow
            token = await create_verification_token(user_id, code)
            plain_url = f"https://t.me/{BOT_USERNAME}?start=verify_{token}"
            short_url = await shorten_url(plain_url)
            await query.edit_message_text(
                "🔐 Verify to get access",
                reply_markup=verification_kb(short_url, plain_url)
            )
        else:
            await query.edit_message_text("Still missing some channels.", reply_markup=query.message.reply_markup)

    elif data == "verify_again":
        # Repeat verification
        code = context.user_data.get("pending_code")
        token = await create_verification_token(user_id, code)
        plain_url = f"https://t.me/{BOT_USERNAME}?start=verify_{token}"
        short_url = await shorten_url(plain_url)
        await query.edit_message_text(
            "🔐 Verify again",
            reply_markup=verification_kb(short_url, plain_url)
        )

    elif data == "time_left":
        expiry = await get_session(user_id)
        if expiry:
            left = expiry - int(time.time())
            await query.edit_message_text(f"⏱ Time Left: {format_time_left(left)}", reply_markup=session_kb())
        else:
            await query.edit_message_text("Session expired.")

    # Add admin callbacks here