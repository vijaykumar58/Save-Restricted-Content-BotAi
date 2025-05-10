import asyncio
import sys
from pathlib import Path
from fastapi import FastAPI
import uvicorn
from pyrogram import Client, idle
from config import config
from handlers import load_handlers

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

# Create FastAPI app for health checks
app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "telegram-bot"}

async def run_web_server():
    """Run the health check web server"""
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=False
    )
    server = uvicorn.Server(config)
    await server.serve()

async def run_bot():
    """Run the Telegram bot"""
    bot = Client(
        "save_restricted_bot",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
        in_memory=True  # Reduces session storage issues
    )
    
    try:
        await bot.start()
        print("✅ Bot started successfully!")
        
        # Load all handlers
        load_handlers(bot)
        
        print("🔄 Bot is running...")
        await idle()
        
    except Exception as e:
        print(f"❌ Bot error: {e}")
    finally:
        await bot.stop()
        print("🛑 Bot stopped")

async def main():
    # Run both web server and bot concurrently
    await asyncio.gather(
        run_web_server(),
        run_bot()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🚨 Received exit signal, shutting down...")
    except Exception as e:
        print(f"🔥 Critical error: {e}")
