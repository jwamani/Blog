from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

sqlite_url = "sqlite:///blog.db"

engine = create_engine(
    sqlite_url,
    connect_args={
        "check_same_thread": False
    }
)  # engine is used to open a connection to the database

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

