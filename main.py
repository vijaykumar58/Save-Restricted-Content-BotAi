import asyncio
import sys
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pyrogram import Client, idle
from pyrogram.errors import FloodWait
import uvicorn
# Assuming config and handlers exist in your project
from config import config
from handlers import load_handlers

app = FastAPI()

# Global health status
# This will be updated by the bot lifecycle and checked by the FastAPI endpoint
health_status = {
    "status": "starting",
    "details": "Initializing bot services"
}

@app.get("/")
async def health_check():
    """Endpoint for health checking."""
    return JSONResponse(content=health_status)

async def run_web_server():
    """Run health check server with enhanced reliability and logging."""
    print("🌐 Starting web server on port 8000...") # Added log
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="warning", # Keep warning to avoid uvicorn's own access logs if access_log=False
        timeout_keep_alive=60,
        access_log=False # Keep False as we handle logging manually
    )
    server = uvicorn.Server(config)
    try:
        print("🌐 Web server binding...") # Added log
        # This await call is blocking until the server is stopped
        await server.serve()
        print("🌐 Web server stopped gracefully.") # Added log - might not be reached on normal exit
    except asyncio.CancelledError:
        print("🌐 Web server task cancelled.") # Added log
        # This exception is expected during graceful shutdown initiated by main()
    except Exception as e:
        print(f"🔥 Web server failed to start or crashed: {type(e).__name__}: {e}") # Added error log
        # Update global health_status to reflect web server failure
        global health_status
        health_status = {
            "status": "web_server_error",
            "details": f"Web server failed: {str(e)}",
            "error": type(e).__name__
        }
        # Depending on criticality, you might want to sys.exit(1) or re-raise
        # For a combined service, failure of one part usually warrants stopping the whole.
        raise # Re-raise to be caught by the main error handling

async def start_bot():
    """Bot startup with comprehensive error handling."""
    global health_status

    bot = Client(
        "save_restricted_bot",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
        in_memory=True
    )

    try:
        # Update health status before attempting to connect
        health_status = {"status": "connecting", "details": "Connecting to Telegram"}
        print("⏳ Connecting to Telegram...") # Added log

        await bot.start()

        # Update health status on successful connection
        health_status = {"status": "running", "details": "Bot active and healthy"}
        print("✅ Bot started successfully!")

        # Load handlers after the bot client is started
        load_handlers(bot)
        print("🔄 Bot is running and handling messages...")
        return bot

    except FloodWait as e:
        # Handle FloodWait specifically, update status and retry
        health_status = {
            "status": "waiting",
            "details": f"Telegram flood wait: {e.value} seconds",
            "retry_in": e.value
        }
        print(f"⏳ Flood wait required: {e.value} seconds. Retrying after delay.")
        await asyncio.sleep(e.value + 5) # Use asyncio.sleep in async context
        return await start_bot()  # Recursive retry

    except Exception as e:
        # Handle any other startup errors
        health_status = {
            "status": "startup_error",
            "details": f"Startup failed: {str(e)}",
            "error": type(e).__name__
        }
        print(f"🔥 Bot startup failed: {type(e).__name__}: {e}") # Added error log
        raise # Re-raise the exception to be caught higher up

async def run_bot():
    """Main bot running loop."""
    global health_status
    bot = None # Initialize bot to None

    try:
        # Start the bot (handles retries internally for FloodWait)
        bot = await start_bot()

        # Idle keeps the bot running and processing updates until stopped
        await idle()

    except Exception as e:
        # Handle runtime errors in the bot's main loop
        health_status = {
            "status": "runtime_error",
            "details": f"Runtime error: {str(e)}",
            "error": type(e).__name__
        }
        print(f"⚠️ Bot runtime error: {type(e).__name__}: {e}")
        # Re-raise or handle as appropriate - raising will lead to graceful shutdown via finally block
        raise

    finally:
        # Ensure the bot client is stopped gracefully
        if bot and bot.is_connected:
            print("🛑 Stopping bot gracefully...") # Added log
            await bot.stop()
            health_status = {"status": "stopped", "details": "Bot shut down gracefully"}
            print("🛑 Bot stopped successfully.") # Added log
        else:
            print("🛑 Bot client not connected or initialized, no stop needed.") # Added log

async def main():
    """Main application entry point, runs bot and web server concurrently."""
    # Use asyncio.create_task to run the web server in the background
    print("🚀 Creating web server task...") # Added log
    server_task = asyncio.create_task(run_web_server())

    try:
        # Await the bot's run loop. This will block until idle() exits or an error occurs.
        print("🚀 Starting bot run loop...") # Added log
        await run_bot()

    except Exception as e:
        # Catch any exceptions that propagate up from run_bot (startup or runtime errors)
        print(f"🔥 Main task caught error: {type(e).__name__}: {e}") # Added log
        # The health_status should already be updated by the originating function (start_bot or run_bot)
        # You might want to perform additional error handling or cleanup here if needed

    finally:
        # Ensure the web server task is cancelled when main exits
        # This is important for graceful shutdown
        print("🛑 Bot run loop finished. Cancelling web server task...") # Added log
        server_task.cancel()
        try:
            # Wait for the server task to actually finish (handle CancellationError)
            print("🛑 Waiting for web server task to finish...") # Added log
            await server_task
            print("🛑 Web server task finished.") # Added log
        except asyncio.CancelledError:
             print("🛑 Web server task cancelled successfully.") # Added log
             pass # This is the expected exception when cancelling a task

# Entry point when the script is executed directly
if __name__ == "__main__":
    # Configure asyncio event loop policy for Windows if necessary
    # This helps prevent issues with subprocesses and loop policies on Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Create a new event loop
    loop = asyncio.new_event_loop()
    # Set the new loop as the current loop
    asyncio.set_event_loop(loop)

    try:
        # Run the main async function until it completes
        loop.run_until_complete(main())

    except KeyboardInterrupt:
        # Handle manual shutdown signal (Ctrl+C)
        health_status = {"status": "stopped", "details": "Manual shutdown"}
        print("\n🛑 Received shutdown signal. Stopping.") # Added log

    except Exception as e:
        # Catch any critical exceptions not handled elsewhere
        health_status = {
            "status": "critical_failure",
            "details": f"Critical failure: {str(e)}",
            "error": type(e).__name__
        }
        print(f"🔥 Critical failure during execution: {type(e).__name__}: {e}") # Added critical error log

    finally:
        # Close the event loop
        print("🚪 Closing event loop.") # Added log
        loop.close()
        print("🚪 All services shut down.")
