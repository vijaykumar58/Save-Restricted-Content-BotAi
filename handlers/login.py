from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid
from config import config
from database import db

def login_handlers(client):
    @client.on_message(filters.command("login") & filters.private)
    async def login_command(client, message: Message):
        user_id = message.from_user.id
        session = await db.get_session(user_id)
        
        if session:
            return await message.reply("You're already logged in!")
        
        await message.reply(
            "Please send your phone number in international format (e.g., +1234567890)"
        )
        client.user_data[user_id] = {"step": "phone"}
    
    @client.on_message(filters.text & filters.private)
    async def handle_phone_number(client, message: Message):
        user_id = message.from_user.id
        user_data = client.user_data.get(user_id, {})
        
        if user_data.get("step") == "phone":
            phone = message.text.strip()
            
            try:
                # Initialize temp client
                temp_client = Client(
                    f"temp_{user_id}",
                    api_id=config.API_ID,
                    api_hash=config.API_HASH,
                    in_memory=True
                )
                await temp_client.connect()
                
                # Send code
                sent_code = await temp_client.send_code(phone)
                
                # Store data
                client.user_data[user_id] = {
                    "step": "code",
                    "phone": phone,
                    "phone_code_hash": sent_code.phone_code_hash,
                    "temp_client": temp_client
                }
                
                await message.reply("Code sent! Please enter the verification code:")
            
            except Exception as e:
                await message.reply(f"Error: {str(e)}")
                if "temp_client" in locals():
                    await temp_client.disconnect()
        
        elif user_data.get("step") == "code":
            code = message.text.strip()
            temp_client = user_data["temp_client"]
            
            try:
                # Sign in
                await temp_client.sign_in(
                    user_data["phone"],
                    user_data["phone_code_hash"],
                    code
                )
                
                # Get session string
                session_string = await temp_client.export_session_string()
                
                # Save to database
                await db.save_session(user_id, session_string)
                
                # Clean up
                await temp_client.disconnect()
                del client.user_data[user_id]
                
                await message.reply("✅ Login successful! Session saved.")
            
            except SessionPasswordNeeded:
                client.user_data[user_id]["step"] = "password"
                await message.reply("Please enter your 2FA password:")
            
            except PhoneCodeInvalid:
                await message.reply("Invalid code. Please try /login again.")
                await temp_client.disconnect()
                del client.user_data[user_id]
        
        elif user_data.get("step") == "password":
            password = message.text.strip()
            temp_client = user_data["temp_client"]
            
            try:
                # Check password
                await temp_client.check_password(password)
                
                # Get session string
                session_string = await temp_client.export_session_string()
                
                # Save to database
                await db.save_session(user_id, session_string)
                
                # Clean up
                await temp_client.disconnect()
                del client.user_data[user_id]
                
                await message.reply("✅ Login successful! Session saved.")
            
            except Exception as e:
                await message.reply(f"Error: {str(e)}")
                await temp_client.disconnect()
                del client.user_data[user_id]
    
    @client.on_message(filters.command("logout") & filters.private)
    async def logout_command(client, message: Message):
        user_id = message.from_user.id
        await db.sessions.delete_one({"user_id": user_id})
        await message.reply("✅ Logged out successfully.")