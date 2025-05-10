import asyncio
from pyrogram import filters
from pyrogram.types import Message
from database import db
from config import config

def batch_handlers(client):
    @client.on_message(filters.command("batch") & filters.private)
    async def batch_download(client, message: Message):
        user_id = message.from_user.id
        is_premium, _ = await db.check_premium(user_id)
        
        if not is_premium:
            return await message.reply(
                "🔒 Premium feature!\n"
                "Subscribe to premium to use batch downloads.\n\n"
                "Use /premium to see available plans."
            )
        
        await message.reply(
            "Please send the message links you want to download (one per line).\n"
            "Example:\n"
            "https://t.me/channel/123\n"
            "https://t.me/channel/124\n\n"
            "Send /done when finished."
        )
        
        client.user_data[user_id] = {"batch": []}
    
    @client.on_message(filters.text & filters.private)
    async def collect_links(client, message: Message):
        user_id = message.from_user.id
        user_data = client.user_data.get(user_id, {})
        
        if "batch" not in user_data:
            return
        
        if message.text.lower() == "/done":
            links = user_data["batch"]
            if not links:
                return await message.reply("No links provided!")
            
            await process_batch(client, message, links)
            del client.user_data[user_id]
            return
        
        # Validate and add link
        if "t.me/" in message.text:
            user_data["batch"].append(message.text.strip())
            await message.reply(f"Added! Total links: {len(user_data['batch'])}")
        else:
            await message.reply("Invalid link format. Please send Telegram message links only.")

async def process_batch(client, message, links):
    total = len(links)
    success = 0
    
    status = await message.reply(f"⏳ Processing {total} links... (0/{total})")
    
    for i, link in enumerate(links, 1):
        try:
            # Process each link here
            # This would be your actual download logic
            await asyncio.sleep(1)  # Simulate processing
            
            success += 1
            await status.edit(f"⏳ Processing {total} links... ({i}/{total})")
        except Exception as e:
            await message.reply(f"Failed to process {link}: {str(e)}")
    
    await status.edit(f"✅ Batch completed!\nSuccess: {success}/{total}")