from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def force_join_kb(channels):
    buttons = []
    for i, ch in enumerate(channels, 1):
        username = ch[1:] if str(ch).startswith("-100") else ch
        url = f"https://t.me/{username}" if not str(ch).startswith("-100") else f"https://t.me/c/{str(ch)[4:]}"
        buttons.append([InlineKeyboardButton(f"Join Channel {i}", url=url)])
    buttons.append([InlineKeyboardButton("🔄 Recheck", callback_data="recheck_force")])
    return InlineKeyboardMarkup(buttons)

def verification_kb(short_url, plain_url):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Open Verification Link", url=short_url)],
        [InlineKeyboardButton("📋 Copy Link (Open in Chrome)", url=plain_url)],
        [InlineKeyboardButton("🔄 Verify Again", callback_data="verify_again")]
    ])

def session_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⏱ Time Left", callback_data="time_left")]])

def admin_main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Link Management", callback_data="admin_links")],
        [InlineKeyboardButton("🔔 Force-Join Channels", callback_data="admin_force")],
        [InlineKeyboardButton("🌐 Shortener Config", callback_data="admin_shortener")],
        [InlineKeyboardButton("📊 Analytics", callback_data="admin_stats")],
    ])