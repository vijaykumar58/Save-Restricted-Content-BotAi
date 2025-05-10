import asyncio
import sys
from pathlib import Path
from fastapi import FastAPI
import uvicorn
from pyrogram import Client
from config import config
from handlers import load_handlers

# Initialize FastAPI app for health checks
app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "running", "bot": "active"}

async def run_web_server():
    """Run the health check server"""
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
    """Main bot execution"""
    bot = Client(
        "save_restricted_bot",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
        in_memory=True
    )
    
    try:
        await bot.start()
        print("✅ Bot started successfully!")
        
        # Manually load all handlers
        load_handlers(bot)
        
        print("🔄 Bot is running and handling messages...")
        await idle()
        
    except Exception as e:
        print(f"❌ Bot error: {e}")
    finally:
        if await bot.is_connected():
            await bot.stop()
            print("🛑 Bot stopped")

async def main():
    # Run both services concurrently
    await asyncio.gather(
        run_web_server(),
        run_bot()
    )

if __name__ == "__main__":
    # Configure asyncio for better stability
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🚨 Received shutdown signal")
    except Exception as e:
        print(f"🔥 Critical failure: {e}")
