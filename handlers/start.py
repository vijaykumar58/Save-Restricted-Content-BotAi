from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import config
from database import db

def start_handler(client):
    @client.on_message(filters.command("start") & filters.private)
    async def start_command(client, message: Message):
        user_id = message.from_user.id
        await db.add_user(user_id)
        
        # Check force subscription
        try:
            member = await client.get_chat_member(config.FORCE_SUB_CHANNEL, user_id)
            if member.status in ["left", "kicked"]:
                raise Exception("Not subscribed")
        except Exception:
            return await message.reply(
                "Please join our channel first to use this bot!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Join Channel", url=f"https://t.me/{config.FORCE_SUB_CHANNEL}")
                ]])
            )
        
        # Welcome message
        is_premium, expiry = await db.check_premium(user_id)
        
        text = (
            "✨ **Welcome to Save Restricted Content Bot** ✨\n\n"
            "I can help you download restricted content from:\n"
            "- Public/Private channels\n"
            "- Groups with forwarding restrictions\n\n"
        )
        
        if is_premium:
            text += f"🌟 **Premium Status**: Active (Expires: {expiry.strftime('%Y-%m-%d')})\n\n"
        else:
            text += "🔹 **Free Tier**: Limited functionality\n"
            text += "💎 Get **Premium** for full features!\n\n"
        
        text += "Use /help to see available commands"
        
        buttons = [
            [InlineKeyboardButton("Get Premium", callback_data="premium_info")],
            [InlineKeyboardButton("Help", callback_data="help")]
        ]
        
        await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))