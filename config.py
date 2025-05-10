import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram API
    API_ID = int(os.getenv("API_ID", 12345))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    STRING_SESSION = os.getenv("STRING_SESSION", "")
    
    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "telegram_bot")
    
    # Owner
    OWNER_ID = list(map(int, os.getenv("OWNER_ID", "123456789").split()))
    
    # Channels
    LOG_CHANNEL = os.getenv("LOG_CHANNEL", savecontentdiscusion)
    FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", allfreecoursesgovtexam)
    
    # Premium
    PREMIUM_PRICES = {
        "1d": 5,    # $5 for 1 day
        "7d": 25,   # $25 for 7 days
        "30d": 80,  # $80 for 30 days
        "90d": 200  # $200 for 90 days
    }

config = Config()
