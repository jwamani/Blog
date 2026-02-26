from fastapi import FastAPI
from v2.src.presentation.api.routes.auth import router as auth_router
from v2.src.presentation.api.routes.posts import router as posts_router
from v2.src.infrastructure.database.connection import engine
from v2.src.infrastructure.database.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(posts_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Clean Architecture Blog API"}