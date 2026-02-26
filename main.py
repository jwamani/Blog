import logging
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

# Support both relative imports (when run as module) and absolute imports (when run directly)
if __package__ is None or __package__ == '':
    # Direct execution: python main.py
    import models
    from database import engine
    from routes.auth import auth_router
    from routes.posts import post_router
    from routes.admin import admin_router
    from routes.users import user_router
else:
    # Module execution: python -m Blog.main or fastapi dev main.py
    from . import models
    from .database import engine
    from .routes.auth import auth_router
    from .routes.posts import post_router
    from .routes.admin import admin_router
    from .routes.users import user_router
    from .routes.images import image_router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="../app.log",
    filemode="a"
)

logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

host = os.getenv("HOST")
port = os.getenv("PORT")


@app.get("/", status_code=200)
def info():
    return {"status": "Healthy"}

app.include_router(router=post_router)
app.include_router(router=auth_router)
app.include_router(router=admin_router)
app.include_router(user_router)
app.include_router(image_router)

if __name__ == "__main__":
    logger.info(f"Starting server at {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=int(port),
        reload=True,
    )
