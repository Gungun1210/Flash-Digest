from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read PostgreSQL database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")  # Ensure you have DATABASE_URL in your .env file

# Initialize the database engine with error logging (echo=True helps with debugging)
engine = create_engine(DATABASE_URL, echo=True)

# Create a SessionLocal class for database session management
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for your models to inherit from
Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db  # This will yield the session for use in other parts of the application
    finally:
        db.close()  # Always close the session when done
