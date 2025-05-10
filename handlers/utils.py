from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from database import db

def utils_handlers(client):
    @client.on_message(filters.command("help") & filters.private)
    async def help_command(client, message: Message):
        is_premium, _ = await db.check_premium(message.from_user.id)
        
        text = "🛠 **Available Commands** 🛠\n\n"
        text += "/start - Start the bot\n"
        text += "/login - Login with your Telegram account\n"
        text += "/logout - Logout from your account\n"
        text += "/premium - View premium plans\n"
        
        if is_premium:
            text += "/batch - Download multiple messages at once\n"
        
        text += "\n📝 **Note**: Some commands require premium subscription"
        
        await message.reply(text)
    
    @client.on_message(filters.command("status") & filters.private)
    async def status_command(client, message: Message):
        user_id = message.from_user.id
        is_premium, expiry = await db.check_premium(user_id)
        
        text = "🔍 **Your Account Status**\n\n"
        text += f"🆔 User ID: `{user_id}`\n"
        text += f"💎 Premium: {'✅ Active' if is_premium else '❌ Inactive'}\n"
        
        if is_premium:
            text += f"📅 Expiry: {expiry.strftime('%Y-%m-%d')}\n"
        
        await message.reply(text)