from pymongo import MongoClient
from config import DATABASE_URL, SESSION_DURATION
import time

client = MongoClient(DATABASE_URL)
db = client.filebot

# Collections
users = db.users
sessions = db.sessions
links = db.links
tokens = db.verification_tokens
settings = db.settings
force_channels = db.force_channels
db_channels = db.database_channels
analytics = db.analytics
bypass_logs = db.bypass_logs

def init_db():
    # Indexes
    sessions.create_index("expiry", expireAfterSeconds=SESSION_DURATION + 3600)
    tokens.create_index("created_at", expireAfterSeconds=3600)

# Settings
async def get_setting(key, default=None):
    doc = settings.find_one({"key": key})
    return doc["value"] if doc else default

async def set_setting(key, value):
    settings.update_one({"key": key}, {"$set": {"value": value}}, upsert=True)

# Sessions
async def get_session(user_id):
    doc = sessions.find_one({"user_id": user_id})
    if doc and doc["expiry"] > int(time.time()):
        return doc["expiry"]
    return None

async def create_session(user_id):
    expiry = int(time.time()) + SESSION_DURATION
    sessions.update_one({"user_id": user_id}, {"$set": {"expiry": expiry}}, upsert=True)
    return expiry

# Force join
async def get_force_channels():
    return [c["channel_id"] for c in force_channels.find()]

async def add_force_channel(channel_id):
    force_channels.update_one({"channel_id": channel_id}, {"$set": {"channel_id": channel_id}}, upsert=True)

async def remove_force_channel(channel_id):
    force_channels.delete_one({"channel_id": channel_id})

# Links
async def save_link(code, type_, channel_id, start_msg, end_msg=None):
    links.update_one(
        {"code": code},
        {"$set": {"type": type_, "channel_id": channel_id, "start_msg": start_msg, "end_msg": end_msg}},
        upsert=True
    )

async def get_link(code):
    return links.find_one({"code": code})

# Verification tokens
async def create_verification_token(user_id, code):
    token = secrets.token_hex(16)
    tokens.insert_one({
        "token": token,
        "user_id": user_id,
        "code": code,
        "created_at": int(time.time())
    })
    return token

async def validate_token(token):
    doc = tokens.find_one_and_delete({"token": token})
    if not doc:
        return None
    time_diff = int(time.time()) - doc["created_at"]
    if time_diff < MIN_VERIFICATION_TIME:
        bypass_logs.insert_one({"user_id": doc["user_id"], "timestamp": int(time.time())})
        return None
    return doc

# Analytics
async def log_action(user_id, action):
    analytics.insert_one({"user_id": user_id, "action": action, "timestamp": int(time.time())})

import secrets

async def apply_caption(message_id, user_id, batch_name=None):  # placeholder, fetch actual file_name if needed
    caption = await get_setting("global_caption", "")
    if not caption:
        return None
    replacements = {
        "{file_name}": "File",  # enhance: fetch real name via bot.get_message
        "{batch_name}": batch_name or "",
        "{user_id}": str(user_id),
        "{expiry_time}": format_time_left(SESSION_DURATION)
    }
    for k, v in replacements.items():
        caption = caption.replace(k, v)
    return caption

async def get_global_caption():

    return await get_setting("global_caption", "")    
