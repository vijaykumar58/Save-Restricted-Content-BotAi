import motor.motor_asyncio
from datetime import datetime, timedelta
from config import config

class Database:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URI)
        self.db = self.client[config.DB_NAME]
        
        # Collections
        self.users = self.db.users
        self.premium = self.db.premium
        self.sessions = self.db.sessions
    
    async def add_user(self, user_id: int):
        await self.users.update_one(
            {"user_id": user_id},
            {"$setOnInsert": {"join_date": datetime.now()}},
            upsert=True
        )
    
    async def save_session(self, user_id: int, session_string: str):
        await self.sessions.update_one(
            {"user_id": user_id},
            {"$set": {
                "session_string": session_string,
                "last_updated": datetime.now()
            }},
            upsert=True
        )
    
    async def get_session(self, user_id: int):
        return await self.sessions.find_one({"user_id": user_id})
    
    async def add_premium(self, user_id: int, duration: str):
        duration_days = int(duration[:-1])
        expiry_date = datetime.now() + timedelta(days=duration_days)
        
        await self.premium.update_one(
            {"user_id": user_id},
            {"$set": {
                "expiry_date": expiry_date,
                "plan": duration,
                "purchase_date": datetime.now()
            }},
            upsert=True
        )
        return expiry_date
    
    async def check_premium(self, user_id: int):
        user = await self.premium.find_one({"user_id": user_id})
        if user and user["expiry_date"] > datetime.now():
            return True, user["expiry_date"]
        return False, None

db = Database()