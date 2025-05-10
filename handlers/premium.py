from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from config import config
from database import db

def premium_handlers(client):
    @client.on_message(filters.command("premium") & filters.private)
    async def premium_info(client, message: Message):
        user_id = message.from_user.id
        is_premium, expiry = await db.check_premium(user_id)
        
        text = "✨ **Premium Plans** ✨\n\n"
        text += "Get access to exclusive features:\n"
        text += "- Unlimited batch downloads\n"
        text += "- Faster download speeds\n"
        text += "- Priority support\n"
        text += "- No ads\n\n"
        
        if is_premium:
            text += f"🌟 **Your Premium Status**: Active (Expires: {expiry.strftime('%Y-%m-%d')}\n\n"
        else:
            text += "🔹 You don't have an active premium subscription\n\n"
        
        text += "Choose a plan:"
        
        buttons = [
            [
                InlineKeyboardButton("1 Day - $5", callback_data="premium_1d"),
                InlineKeyboardButton("7 Days - $25", callback_data="premium_7d")
            ],
            [
                InlineKeyboardButton("30 Days - $80", callback_data="premium_30d"),
                InlineKeyboardButton("90 Days - $200", callback_data="premium_90d")
            ]
        ]
        
        await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))
    
    @client.on_callback_query(filters.regex("^premium_"))
    async def premium_callback(client, callback: CallbackQuery):
        plan = callback.data.split("_")[1]
        user_id = callback.from_user.id
        
        if plan not in ["1d", "7d", "30d", "90d"]:
            return await callback.answer("Invalid plan selected")
        
        # In a real bot, you would integrate payment processing here
        # For this example, we'll just activate premium
        
        expiry = await db.add_premium(user_id, plan)
        
        await callback.message.edit(
            f"✅ Premium activated successfully!\n"
            f"Plan: {plan}\n"
            f"Expires: {expiry.strftime('%Y-%m-%d')}",
            reply_markup=None
        )
        
        await callback.answer()