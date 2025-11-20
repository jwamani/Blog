from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# sqlite_url = "sqlite:///blog.db"
db_url = "postgresql://worms:worms@localhost:5432/blog"

engine = create_engine(
    db_url,
)  # engine is used to open a connection to the database

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

