# backend/sagemaker_train.py
import random
from datetime import datetime, timedelta
import csv
# backend/sagemaker_train.py (continued)
import sagemaker
from sagemaker import get_execution_role
from sagemaker.estimator import Estimator
import os;
from dotenv import load_dotenv
load_dotenv()
# Previous code for generating data (above) goes here

# SageMaker setup
role = os.getenv("SAGEMAKER_ROLE_ARN")
sess = sagemaker.Session()
bucket = "task-allocation"  # Replace with your S3 bucket name
prefix = "task-allocation"

# Upload data to S3
training_data_uri = sess.upload_data(path="training_data.csv", bucket=bucket, key_prefix=prefix)
print(f"Data uploaded to: {training_data_uri}")

# Define Linear Learner estimator
linear = Estimator(
    image_uri=sagemaker.image_uris.retrieve("linear-learner", sess.boto_region_name),
    role=role,
    instance_count=1,
    instance_type="ml.m5.large",
    output_path=f"s3://{bucket}/{prefix}/output",
    sagemaker_session=sess
)

# Hyperparameters
linear.set_hyperparameters(
    feature_dim=3,  # Number of features
    predictor_type="regressor",
    mini_batch_size=100
)

# Train the model
linear.fit({"train": training_data_uri})
print("Model training completed")

# Deploy the model
predictor = linear.deploy(initial_instance_count=1, instance_type="ml.t2.medium")
print(f"Endpoint deployed: {predictor.endpoint_name}")

# Save endpoint name for backend use
with open("endpoint_name.txt", "w") as f:
    f.write(predictor.endpoint_name)
# Possible skills
skills_list = ["Python", "Java", "React", "AWS", "Docker", "Machine Learning", "Data Analysis"]

# Generate synthetic employees
num_employees = 50
employees = []
for i in range(num_employees):
    num_skills = random.randint(1, 5)
    employee_skills = random.sample(skills_list, num_skills)
    skills = {skill: random.randint(1, 5) for skill in employee_skills}
    start_date = datetime.now() + timedelta(days=random.randint(0, 365))
    end_date = start_date + timedelta(days=random.randint(1, 30))
    availability = [{"available_from": start_date.isoformat(), "available_to": end_date.isoformat()}]
    employees.append({"id": f"emp{i}", "skills": skills, "availability": availability})

# Generate synthetic tasks
num_tasks = 100
tasks = []
for i in range(num_tasks):
    num_required_skills = random.randint(1, 3)
    required_skills = random.sample(skills_list, num_required_skills)
    start_date = datetime.now() + timedelta(days=random.randint(0, 365))
    due_date = start_date + timedelta(days=random.randint(1, 30))
    tasks.append({"id": f"task{i}", "required_skills": required_skills, "start_date": start_date.isoformat(), "due_date": due_date.isoformat()})

# Generate training data
training_data = []
for task in tasks:
    for emp in employees:
        # Features
        required_skills = set(task["required_skills"])
        employee_skills = set(emp["skills"].keys())
        matching_skills = required_skills & employee_skills
        skill_match_count = len(matching_skills)
        required_skills_count = len(required_skills)
        skill_match_ratio = skill_match_count / required_skills_count if required_skills_count > 0 else 0
        avg_proficiency = (
            sum(emp["skills"][skill] for skill in matching_skills) / skill_match_count
            if skill_match_count > 0 else 0
        )

        task_start = datetime.fromisoformat(task["start_date"])
        task_end = datetime.fromisoformat(task["due_date"])
        task_duration = (task_end - task_start).total_seconds()
        availability_overlap = 0
        for avail in emp["availability"]:
            avail_start = datetime.fromisoformat(avail["available_from"])
            avail_end = datetime.fromisoformat(avail["available_to"])
            overlap_start = max(task_start, avail_start)
            overlap_end = min(task_end, avail_end)
            overlap = max(0, (overlap_end - overlap_start).total_seconds())
            availability_overlap = max(availability_overlap, overlap / task_duration)

        # Target score
        target_score = skill_match_ratio * (avg_proficiency / 5) * availability_overlap
        training_data.append([skill_match_ratio, availability_overlap, avg_proficiency, target_score])

# Save to CSV
with open("training_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["skill_match_ratio", "availability_overlap", "avg_proficiency", "target_score"])
    writer.writerows(training_data)

print("Training data generated: training_data.csv")