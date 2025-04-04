from fastapi import APIRouter, HTTPException, Request
from ..models.user import User
from ..services.database import get_collection
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=User)
async def create_user(user: User, request: Request):
    collection = await get_collection("users", request)
    
    # Check if user with this clerk_id already exists
    existing_user = await collection.find_one({"clerk_id": user.clerk_id})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this clerk_id already exists")
    
    # Insert the new user
    user_dict = user.dict()
    result = await collection.insert_one(user_dict)
    
    if result.inserted_id:
        # Return the user with the id field set
        user_dict["id"] = str(result.inserted_id)
        return User(**user_dict)
    
    raise HTTPException(status_code=500, detail="Failed to create user")

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, request: Request):
    collection = await get_collection("users", request)
    
    # Try to find by ObjectId first
    try:
        user = await collection.find_one({"_id": ObjectId(user_id)})
    except:
        # If not a valid ObjectId, try to find by clerk_id
        user = await collection.find_one({"clerk_id": user_id})
    
    if user:
        user["id"] = str(user["_id"])
        return User(**user)
    
    raise HTTPException(status_code=404, detail="User not found")

@router.patch("/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: dict, request: Request):
    collection = await get_collection("users", request)
    
    try:
        # Try as ObjectId first
        object_id = ObjectId(user_id)
        updated_user = await collection.find_one_and_update(
            {"_id": object_id}, {"$set": user_update}, return_document=True
        )
    except:
        # If not a valid ObjectId, try to find by clerk_id
        updated_user = await collection.find_one_and_update(
            {"clerk_id": user_id}, {"$set": user_update}, return_document=True
        )
    
    if updated_user:
        updated_user["id"] = str(updated_user["_id"])
        return User(**updated_user)
    
    raise HTTPException(status_code=404, detail="User not found")