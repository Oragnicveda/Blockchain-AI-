import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    CRUNCHBASE_API_KEY = os.getenv('CRUNCHBASE_API_KEY', '')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 5))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
    RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', 1))
    
    OUTPUT_DIR = Path('output')
    
    CATEGORIES = ['blockchain', 'crypto', 'web3', 'ai', 'defi', 'nft']
    
    STARTUP_DATABASES = [
        'https://www.crunchbase.com',
        'https://www.producthunt.com',
        'https://angel.co',
    ]
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    ]
    
    @classmethod
    def validate(cls):
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        return True
