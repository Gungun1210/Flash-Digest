# test_db.py
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()  # Loads from .env

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute("SELECT current_database();")
        print(f"✅ Connected to DB: {result.scalar()}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
