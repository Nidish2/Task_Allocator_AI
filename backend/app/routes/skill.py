from fastapi import APIRouter, HTTPException, Request
from ..models.skill import Skill
from ..services.database import get_collection
from bson import ObjectId
from typing import List

router = APIRouter()

@router.post("/", response_model=Skill)
async def add_skill(skill: Skill, request: Request):
    collection = await get_collection("skills", request)
    
    # Check if user exists
    users_collection = await get_collection("users", request)
    user = None
    
    # Try to find by ObjectId
    try:
        user = await users_collection.find_one({"_id": ObjectId(skill.user_id)})
    except:
        # If not valid ObjectId, try to find by clerk_id
        user = await users_collection.find_one({"clerk_id": skill.user_id})
    
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Check if this skill already exists for this user
    existing_skill = await collection.find_one({
        "user_id": skill.user_id,
        "skill_name": skill.skill_name
    })
    
    if existing_skill:
        # Update existing skill
        result = await collection.update_one(
            {"_id": existing_skill["_id"]},
            {"$set": {"proficiency_level": skill.proficiency_level}}
        )
        if result.modified_count > 0:
            updated_skill = await collection.find_one({"_id": existing_skill["_id"]})
            updated_skill["id"] = str(updated_skill["_id"])
            return Skill(**updated_skill)
    else:
        # Insert new skill
        skill_dict = skill.dict()
        result = await collection.insert_one(skill_dict)
        if result.inserted_id:
            skill_dict["id"] = str(result.inserted_id)
            return Skill(**skill_dict)
    
    raise HTTPException(status_code=500, detail="Failed to add skill")

@router.get("/{user_id}", response_model=List[Skill])
async def get_skills(user_id: str, request: Request):
    collection = await get_collection("skills", request)
    
    # Try to match by user_id directly first
    skills = await collection.find({"user_id": user_id}).to_list(None)
    
    # If no skills found and the ID looks like it could be an ObjectId, try to match by clerk_id
    if not skills and len(user_id) == 24:
        try:
            # Find the user by ObjectId to get their clerk_id
            users_collection = await get_collection("users", request)
            user = await users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                # Now look for skills with that clerk_id
                skills = await collection.find({"user_id": user["clerk_id"]}).to_list(None)
        except:
            pass
    
    result_skills = []
    for skill in skills:
        skill["id"] = str(skill["_id"])
        result_skills.append(Skill(**skill))
    
    return result_skills
