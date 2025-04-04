from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
# Import router modules
from app.routes import user, task, skill, availability

# Load environment variables
load_dotenv()
uri = os.getenv("MONGO_URL")

# Lifespan context manager for MongoDB connection
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize MongoDB client
    app.mongodb = motor.motor_asyncio.AsyncIOMotorClient(uri).task_allocation_db
    print("MongoDB client connected")  # For debugging
    yield
    # Shutdown: Close MongoDB client
    app.mongodb.client.close()
    print("MongoDB client closed")  # For debugging

# Create FastAPI instance with lifespan
app = FastAPI(title="Task Allocation API", lifespan=lifespan)

# Configure CORS (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with proper prefixes
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(task.router, prefix="/tasks", tags=["tasks"])
app.include_router(skill.router, prefix="/skills", tags=["skills"])
app.include_router(availability.router, prefix="/availability", tags=["availability"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Task Allocation API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)