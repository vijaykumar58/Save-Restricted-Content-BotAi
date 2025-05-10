import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from pyrogram import Client, idle
from config import config
from handlers import load_handlers

async def main():
    bot = Client(
        "save_restricted_bot",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
        plugins={"root": "handlers"}
    )
    
    try:
        await bot.start()
        print("✅ Bot started successfully!")
        
        # Load all handlers
        load_handlers(bot)
        
        print("🔄 Bot is running...")
        await idle()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await bot.stop()
        print("🛑 Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())
