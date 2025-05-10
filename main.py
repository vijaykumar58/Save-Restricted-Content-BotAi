import asyncio
import sys
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pyrogram import Client, idle
from pyrogram.errors import FloodWait
import uvicorn
from config import config
from handlers import load_handlers

app = FastAPI()

# Global health status
health_status = {
    "status": "starting",
    "details": "Initializing bot services"
}

@app.get("/")
async def health_check():
    return JSONResponse(content=health_status)

async def run_web_server():
    """Run health check server with enhanced reliability"""
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="warning",
        timeout_keep_alive=60,
        access_log=False
    )
    server = uvicorn.Server(config)
    await server.serve()

async def start_bot():
    """Bot startup with comprehensive error handling"""
    global health_status
    
    bot = Client(
        "save_restricted_bot",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
        in_memory=True
    )
    
    try:
        # Update health status
        health_status = {"status": "connecting", "details": "Connecting to Telegram"}
        
        await bot.start()
        health_status = {"status": "running", "details": "Bot active and healthy"}
        print("✅ Bot started successfully!")
        
        load_handlers(bot)
        print("🔄 Bot is running and handling messages...")
        return bot
        
    except FloodWait as e:
        health_status = {
            "status": "waiting",
            "details": f"Telegram flood wait: {e.value} seconds",
            "retry_in": e.value
        }
        print(f"⏳ Flood wait required: {e.value} seconds")
        time.sleep(e.value + 5)
        return await start_bot()  # Retry
        
    except Exception as e:
        health_status = {
            "status": "error",
            "details": f"Startup failed: {str(e)}",
            "error": type(e).__name__
        }
        raise

async def run_bot():
    """Main bot running loop"""
    global health_status
    bot = None
    
    try:
        bot = await start_bot()
        await idle()
        
    except Exception as e:
        health_status = {
            "status": "error",
            "details": f"Runtime error: {str(e)}",
            "error": type(e).__name__
        }
        print(f"⚠️ Bot runtime error: {type(e).__name__}: {e}")
    finally:
        if bot and bot.is_connected:
            await bot.stop()
            health_status = {"status": "stopped", "details": "Bot shut down gracefully"}
            print("🛑 Bot stopped gracefully")

async def main():
    """Main application entry point"""
    server_task = asyncio.create_task(run_web_server())
    
    try:
        await run_bot()
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    # Configure asyncio for maximum stability
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        health_status = {"status": "stopped", "details": "Manual shutdown"}
        print("\n🛑 Received shutdown signal")
    except Exception as e:
        health_status = {
            "status": "error",
            "details": f"Critical failure: {str(e)}",
            "error": type(e).__name__
        }
        print(f"🔥 Critical failure: {type(e).__name__}: {e}")
    finally:
        loop.close()
        print("🚪 All services shut down")
