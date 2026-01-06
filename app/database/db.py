from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import dotenv

from app.database.models import Base

dotenv.load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:password@db:5432/Data")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
LocalSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)