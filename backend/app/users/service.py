from bson import ObjectId
from app.core.database import get_mongodb
from app.auth.models import UserInDB
from bson.errors import InvalidId

async def get_user_by_id(user_id: str) -> UserInDB | None:
    try:
        obj_id = ObjectId(user_id)
    except InvalidId:
        return None
    
    db = await get_mongodb()
    user_dict = await db.users.find_one({"_id": obj_id})
    if user_dict:
        return UserInDB(**user_dict)
    return None
