# backend/app/services/task_allocation.py
import csv
from io import StringIO
import boto3
from datetime import datetime
from pymongo.collection import Collection
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from ..services.database import get_collection

# Load SageMaker endpoint name (from training step)
with open("../../endpoint_name.txt", "r") as f:
    ENDPOINT_NAME = f.read().strip()

runtime = boto3.client("sagemaker-runtime")

def compute_features(task: dict, employee: dict) -> list:
    """Compute features for a task-employee pair."""
    required_skills = set(task["required_skills"])
    employee_skills = {skill["skill_name"]: skill["proficiency_level"] for skill in employee["skills"]}
    matching_skills = required_skills & set(employee_skills.keys())
    skill_match_count = len(matching_skills)
    required_skills_count = len(required_skills)
    skill_match_ratio = skill_match_count / required_skills_count if required_skills_count > 0 else 0
    avg_proficiency = (
        sum(employee_skills[skill] for skill in matching_skills) / skill_match_count
        if skill_match_count > 0 else 0
    )

    task_start = datetime.fromisoformat(task["start_date"])
    task_end = datetime.fromisoformat(task["due_date"])
    task_duration = (task_end - task_start).total_seconds()
    availability_overlap = 0
    for avail in employee["availability"]:
        avail_start = datetime.fromisoformat(avail["available_from"])
        avail_end = datetime.fromisoformat(avail["available_to"])
        overlap_start = max(task_start, avail_start)
        overlap_end = min(task_end, avail_end)
        overlap = max(0, (overlap_end - overlap_start).total_seconds())
        availability_overlap = max(availability_overlap, overlap / task_duration)

    return [skill_match_ratio, availability_overlap, avg_proficiency]

async def assign_task(task_id: str):
    """Assign a task to the most suitable employee using SageMaker."""
    # Fetch task
    task_collection: Collection = await get_collection("tasks")
    task = await task_collection.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise ValueError("Task not found")

    # Fetch employees
    user_collection: Collection = await get_collection("users")
    employees = await user_collection.find({"role": "employee"}).to_list(None)
    if not employees:
        raise ValueError("No employees available")

    # Fetch skills and availability
    skill_collection: Collection = await get_collection("skills")
    availability_collection: Collection = await get_collection("availability")
    employee_data = []
    for emp in employees:
        skills = await skill_collection.find({"user_id": str(emp["_id"])}).to_list(None)
        availability = await availability_collection.find({"user_id": str(emp["_id"])}).to_list(None)
        employee_data.append({"id": str(emp["_id"]), "skills": skills, "availability": availability})

    # Compute features for each employee
    features_list = [compute_features(task, emp) for emp in employee_data]

    # Prepare CSV for SageMaker batch inference
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerows(features_list)
    csv_data = csv_buffer.getvalue()

    # Call SageMaker endpoint
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="text/csv",
        Body=csv_data
    )
    scores = [float(score) for score in response["Body"].read().decode("utf-8").split("\n") if score]

    # Assign to the highest-scoring employee
    best_index = scores.index(max(scores))
    best_employee_id = employee_data[best_index]["id"]
    await task_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"assigned_to": best_employee_id}})
    print(f"Task {task_id} assigned to employee {best_employee_id}")