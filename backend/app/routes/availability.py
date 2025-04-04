from fastapi import APIRouter, HTTPException, Request
from ..models.availability import Availability
from ..services.database import get_collection
from bson import ObjectId
from typing import List
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.post("/", response_model=Availability)
async def set_availability(availability: Availability, request: Request):
    """Set a user's availability after verifying the user exists."""
    collection = await get_collection("availability", request)
    
    # Check if user exists
    users_collection = await get_collection("users", request)
    user = None
    
    try:
        # Attempt to interpret user_id as an ObjectId
        user = await users_collection.find_one({"_id": ObjectId(availability.user_id)})
    except ValueError:
        # If not a valid ObjectId, assume it's a clerk_id
        user = await users_collection.find_one({"clerk_id": availability.user_id})
    except Exception as e:
        logger.error(f"Error checking user existence: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while verifying user")
    
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Insert the availability
    availability_dict = availability.model_dump()
    try:
        result = await collection.insert_one(availability_dict)
    except Exception as e:
        logger.error(f"Failed to insert availability: {e}")
        raise HTTPException(status_code=500, detail="Failed to set availability")
    
    if result.inserted_id:
        availability_dict["id"] = str(result.inserted_id)
        return Availability(**availability_dict)
    
    raise HTTPException(status_code=500, detail="Failed to set availability")

@router.get("/{user_id}", response_model=List[Availability])
async def get_availability(user_id: str, request: Request):
    """Retrieve a user's availability, supporting both ObjectId and clerk_id."""
    collection = await get_collection("availability", request)
    
    # Assume user_id in availability is clerk_id by default
    availabilities = await collection.find({"user_id": user_id}).to_list(None)
    
    # If no availabilities found and user_id might be an ObjectId, resolve clerk_id
    if not availabilities and len(user_id) == 24:
        try:
            users_collection = await get_collection("users", request)
            user = await users_collection.find_one({"_id": ObjectId(user_id)})
            if user and "clerk_id" in user:
                logger.info(f"Resolved ObjectId {user_id} to clerk_id {user['clerk_id']}")
                availabilities = await collection.find({"user_id": user["clerk_id"]}).to_list(None)
        except ValueError:
            logger.debug(f"User_id {user_id} is not a valid ObjectId, skipping clerk_id lookup")
        except Exception as e:
            logger.error(f"Error resolving clerk_id from ObjectId {user_id}: {e}")
    
    result_availabilities = []
    for avail in availabilities:
        try:
            avail["id"] = str(avail["_id"])
            # Remove _id to avoid Pydantic validation issues if not in model
            avail.pop("_id", None)
            result_availabilities.append(Availability(**avail))
        except Exception as e:
            logger.error(f"Error parsing availability document {avail}: {e}")
            raise HTTPException(status_code=500, detail="Error processing availability data")
    
    return result_availabilities