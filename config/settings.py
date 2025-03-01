from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    """Configuration settings for the application"""
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    MONGODB_URI = os.getenv('MONGODB_URI')
    DEFAULT_PROFICIENCY = "Intermediate (Familiar with basic concepts)"
    PROFICIENCY_LEVELS = [
        "Beginner (New to DSA)",
        "Intermediate (Familiar with basic concepts)",
        "Advanced (Comfortable with most DSA topics)"
    ]