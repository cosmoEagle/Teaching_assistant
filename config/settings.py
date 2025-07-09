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
    
    # Rate limiting configuration
    ENABLE_RATE_LIMITING = os.getenv('ENABLE_RATE_LIMITING', 'false').lower() == 'true'
    MAX_QUERIES_PER_HOUR = int(os.getenv('MAX_QUERIES_PER_HOUR', '50'))
    MAX_TOKENS_PER_QUERY = int(os.getenv('MAX_TOKENS_PER_QUERY', '4000'))
    RATE_LIMIT_STORAGE_TYPE = os.getenv('RATE_LIMIT_STORAGE_TYPE', 'session')  # 'session' or 'database'