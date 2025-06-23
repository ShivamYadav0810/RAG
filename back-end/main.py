from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import chats, conversations, health, upload, users
from config import settings
from utils.logger import setup_logging

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION
    )

    # Setup logging
    setup_logging()

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(chats.router)
    app.include_router(conversations.router)
    app.include_router(health.router)
    app.include_router(users.router)
    app.include_router(upload.router)

    @app.get("/")
    async def root():
        return {"message": f"{settings.APP_NAME} is running", "status": "healthy"}

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )