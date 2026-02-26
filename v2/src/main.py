from fastapi import FastAPI
from presentation.api.routes.auth import router as auth_router
from presentation.api.routes.posts import router as posts_router
from infrastructure.database.connection import engine
from infrastructure.database.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(posts_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Clean Architecture Blog API"}