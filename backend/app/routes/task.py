from fastapi import APIRouter, HTTPException, Depends, Request
from ..models.task import Task
from ..services.database import get_collection
from bson import ObjectId
from typing import List
import json

router = APIRouter()

# Updated dependency to enforce supervisor-only access
async def check_supervisor(user_id: str, request: Request):
    collection = await get_collection("users", request)
    # Try lookup by ObjectId
    try:
        user = await collection.find_one({"_id": ObjectId(user_id)})
    except:
        # If not valid ObjectId, try by clerk_id
        user = await collection.find_one({"clerk_id": user_id})
    
    if not user or user.get("role") != "supervisor":
        raise HTTPException(status_code=403, detail="Only supervisors can create tasks")
    return user

@router.post("/", response_model=Task)
async def create_task(task: Task, request: Request):
    # Check if supervisor exists
    users_collection = await get_collection("users", request)
    supervisor = await users_collection.find_one({"clerk_id": task.supervisor_id})
    if not supervisor or supervisor.get("role") != "supervisor":
        raise HTTPException(status_code=400, detail="Invalid supervisor")
    
    collection = await get_collection("tasks", request)
    task_dict = task.dict()
    result = await collection.insert_one(task_dict)
    
    if result.inserted_id:
        task_dict["id"] = str(result.inserted_id)
        return Task(**task_dict)
    raise HTTPException(status_code=500, detail="Failed to create task")

@router.get("/", response_model=List[Task])
async def get_tasks(user_id: str, role: str, request: Request):
    collection = await get_collection("tasks", request)
    
    if role == "supervisor":
        tasks = await collection.find({"supervisor_id": user_id}).to_list(None)
    elif role == "employee":
        tasks = await collection.find({"assigned_to": user_id}).to_list(None)
    else:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    result_tasks = []
    for task in tasks:
        task["id"] = str(task["_id"])
        # Convert ObjectId to string for JSON serialization
        task_dict = json.loads(json.dumps(task, default=str))
        result_tasks.append(Task(**task_dict))
    
    return result_tasks

@router.patch("/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: dict, request: Request):
    collection = await get_collection("tasks", request)
    
    # Handle date fields properly if they exist in the update
    for date_field in ["due_date", "start_date"]:
        if date_field in task_update and isinstance(task_update[date_field], str):
            # The model will handle the conversion when we return the Task
            pass
    
    updated_task = await collection.find_one_and_update(
        {"_id": ObjectId(task_id)}, {"$set": task_update}, return_document=True
    )
    
    if updated_task:
        updated_task["id"] = str(updated_task["_id"])
        # Convert ObjectId to string for JSON serialization
        updated_task_dict = json.loads(json.dumps(updated_task, default=str))
        return Task(**updated_task_dict)
    
    raise HTTPException(status_code=404, detail="Task not found")

