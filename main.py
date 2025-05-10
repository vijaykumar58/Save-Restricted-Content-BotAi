import asyncio
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
    
    # Start the bot
    await bot.start()
    print("Bot started successfully!")
    
    # Load all handlers
    await load_handlers(bot)
    
    # Run until stopped
    await idle()
    
    # Stop the bot
    await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())