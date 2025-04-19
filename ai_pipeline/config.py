from dotenv import load_dotenv
import os

# Load variables from .env file into environment
load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    MODEL_NAME = os.getenv("MODEL_NAME", "llama3-8b-8192")  # default Groq model

# Create a settings instance
settings = Settings()
