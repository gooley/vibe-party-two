import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1'
    DEFAULT_MODEL = 'google/gemini-2.0-flash-exp'
    PHOTO_DIRECTORY = os.getenv('PHOTO_DIRECTORY', './photos')
    TOURNAMENT_DATA_FILE = 'tournament_results.json'
    
    # Tournament settings
    TOURNAMENT_BRACKET_SIZE = 8  # Number of photos per round comparison
    MIN_PHOTOS_FOR_NEXT_ROUND = 2  # Minimum photos to advance