import aiohttp
import secrets
import time
from config import SHORTENER_API_URL, SHORTENER_API_KEY, BOT_USERNAME

async def shorten_url(url):
    if not SHORTENER_API_URL:
        return url
    async with aiohttp.ClientSession() as session:
        payload = {"url": url, "key": SHORTENER_API_KEY}
        async with session.post(SHORTENER_API_URL, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("shortened_url", url)
            return url

def generate_code(prefix="file"):
    return f"{prefix}_{secrets.token_hex(8)}"

def format_time_left(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h}h {m}m"