import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://prediction_user:prediction_pass@postgres:5432/prediction_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-to-a-secret-key-in-production")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# הגדרות נוספות
API_V1_PREFIX = "/api/v1"
PROJECT_NAME = "Prediction Point System"
