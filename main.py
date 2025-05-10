import asyncio
import sys
import time
from fastapi import FastAPI
from pyrogram import Client, idle
from pyrogram.errors import FloodWait
import uvicorn
from config import config
from handlers import load_handlers

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "ok", "bot": "initializing"}

async def run_web_server():
    """Run the health check server separately"""
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="warning",
        access_log=False
    )
    server = uvicorn.Server(config)
    await server.serve()

async def start_bot_with_retry():
    """Handle flood wait with exponential backoff"""
    bot = Client(
        "save_restricted_bot",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
        in_memory=True
    )
    
    max_retries = 5
    base_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            await bot.start()
            print("✅ Bot started successfully!")
            return bot
            
        except FloodWait as e:
            wait_time = e.value
            print(f"⏳ Attempt {attempt + 1}: Flood wait required - {wait_time} seconds")
            
            # Update health check status during wait
            @app.get("/")
            async def health_check():
                return {"status": "waiting", "retry_in": wait_time, "attempt": attempt + 1}
            
            time.sleep(wait_time + base_delay * (attempt + 1))
            
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {type(e).__name__}: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(base_delay * (attempt + 1))
    
    raise Exception("Failed to start bot after multiple attempts")

async def run_bot():
    bot = await start_bot_with_retry()
    
    # Update health check status
    @app.get("/")
    async def health_check():
        return {"status": "running", "bot": "active"}
    
    try:
        load_handlers(bot)
        print("🔄 Bot is running and handling messages...")
        await idle()
        
    except Exception as e:
        print(f"⚠️ Bot runtime error: {type(e).__name__}: {e}")
    finally:
        if bot.is_connected:
            await bot.stop()
            print("🛑 Bot stopped gracefully")

async def main():
    # Start web server immediately
    server_task = asyncio.create_task(run_web_server())
    
    # Then start bot with retry logic
    try:
        await run_bot()
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    # Configure asyncio policy
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n🛑 Received shutdown signal")
    except Exception as e:
        print(f"🔥 Critical failure: {type(e).__name__}: {e}")
    finally:
        loop.close()
        print("🚪 All services shut down")
