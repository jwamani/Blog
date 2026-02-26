from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# sqlite_url = "sqlite:///blog.db"
db_url = "postgresql://worms:worms@localhost:5432/blog"

engine = create_engine(
    db_url,
    pool_pre_ping=True
)  # engine is used to open a connection to the database

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
