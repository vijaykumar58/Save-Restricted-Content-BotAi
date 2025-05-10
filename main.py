import asyncio
import sys
from pathlib import Path
from fastapi import FastAPI
import uvicorn
from pyrogram import Client, idle
from pyrogram.errors import FloodWait
import time
from config import config
from handlers import load_handlers

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "running"}

async def run_web_server():
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="warning",
        access_log=False
    )
    server = uvicorn.Server(config)
    await server.serve()

async def run_bot():
    bot = Client(
        "save_restricted_bot",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
        in_memory=True
    )
    
    try:
        # Handle flood wait errors
        try:
            await bot.start()
        except FloodWait as e:
            print(f"⏳ Flood wait required: {e.value} seconds")
            time.sleep(e.value + 5)  # Add buffer time
            await bot.start()
            
        print("✅ Bot started successfully!")
        load_handlers(bot)
        print("🔄 Bot is running...")
        await idle()
        
    except Exception as e:
        print(f"❌ Bot error: {type(e).__name__}: {e}")
    finally:
        if hasattr(bot, 'is_connected') and bot.is_connected:  # Fixed connection check
            await bot.stop()
            print("🛑 Bot stopped")

async def main():
    # Run services with proper error handling
    try:
        await asyncio.gather(
            run_web_server(),
            run_bot()
        )
    except asyncio.CancelledError:
        print("🚨 Received shutdown signal")
    except Exception as e:
        print(f"🔥 Critical error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    # Configure asyncio policy for stability
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run with proper cleanup
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n🛑 Manual shutdown requested")
    finally:
        loop.close()
