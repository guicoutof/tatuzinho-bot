import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "https://tatuzinho.onrender.com")
PROXY_URL = os.getenv("PROXY_URL")
