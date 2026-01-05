import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "5298223577").split(",") if x]
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb+srv://baleny:zpQKH66B4AaYldIx@cluster0.ichdp1p.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # mongodb+srv://...
SHORTENER_API_URL = os.getenv("SHORTENER_API_URL")
SHORTENER_API_KEY = os.getenv("SHORTENER_API_KEY")
SESSION_DURATION = 21600  # 6 hours
MIN_VERIFICATION_TIME = 35
BOT_USERNAME = os.getenv("BOT_USERNAME", "")  # without @