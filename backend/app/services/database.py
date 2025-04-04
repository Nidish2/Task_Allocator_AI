from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorCollection

async def get_collection(collection_name: str, request: Request = None) -> AsyncIOMotorCollection:
    """
    Get a MongoDB collection from the application state.
    This function expects the MongoDB client to be attached to the app object.
    """
    from fastapi import FastAPI
    import inspect
    
    # Get the current FastAPI app instance
    current_frame = inspect.currentframe()
    while current_frame:
        if 'app' in current_frame.f_locals and isinstance(current_frame.f_locals['app'], FastAPI):
            app = current_frame.f_locals['app']
            break
        current_frame = current_frame.f_back
    
    # If we have a request object, get the app from it
    if request:
        app = request.app
    
    # Make sure we have a MongoDB client
    if not hasattr(app, 'mongodb'):
        raise RuntimeError("MongoDB client not initialized. Make sure to call startup_db_client.")
    
    # Return the collection
    return app.mongodb[collection_name]