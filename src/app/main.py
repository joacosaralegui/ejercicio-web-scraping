from fastapi import FastAPI

from app.api import endpoints
from app.db import database

def create_app():

    # Fast API app
    app = FastAPI()


    # Connect to database on startup
    @app.on_event("startup")
    async def startup():
        await database.connect()

    # Disconnect from database on shutdown
    @app.on_event("shutdown")
    async def shutdown():
        await database.disconnect()

    # Include all endpoints
    app.include_router(endpoints.router, prefix="", tags=["main"])

    return app

app = create_app()