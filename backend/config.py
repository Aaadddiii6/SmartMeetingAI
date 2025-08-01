"""
Configuration module for the SmartMeetingAI backend
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    UPLOAD_FOLDER = 'backend/uploads'
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'}
    
    # Background Processing Configuration
    THREAD_POOL_SIZE = 4
    
    # Storage Configuration
    STORAGE_BACKEND = os.environ.get('STORAGE_BACKEND') or 'local'
    
    # API Keys
    QUICKREEL_API_KEY = os.environ.get('QUICKREEL_API_KEY') or None
    QUICKREEL_API_URL = os.environ.get('QUICKREEL_API_URL') or 'https://mango.quickreel.io/api/v2'
    
    # AssemblyAI for transcript generation
    ASSEMBLYAI_API_KEY = os.environ.get('ASSEMBLYAI_API_KEY') or None
    
    # OpenAI for blog and poster generation
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or None
    
    # RunwayML for enhanced poster generation
    RUNWAYML_API_KEY = os.environ.get('RUNWAYML_API_KEY') or None
    RUNWAYML_API_URL = os.environ.get('RUNWAYML_API_URL') or 'https://api.runwayml.com/v1'
    
    # Stability AI for better poster generation
    STABILITYAI_API_KEY = os.environ.get('STABILITYAI_API_KEY') or None
    
    # Canva API for template-based poster generation
    CANVA_API_KEY = os.environ.get('CANVA_API_KEY') or None
    CANVA_API_URL = os.environ.get('CANVA_API_URL') or 'https://api.canva.com/v1'
    
    # Instagram API (for later)
    INSTAGRAM_ACCESS_TOKEN = os.environ.get('INSTAGRAM_ACCESS_TOKEN') or None
    INSTAGRAM_BUSINESS_ACCOUNT_ID = os.environ.get('INSTAGRAM_BUSINESS_ACCOUNT_ID') or None
    FACEBOOK_PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID') or None
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or None
    
    # File Processing
    MAX_VIDEO_DURATION = 7200  # 2 hours in seconds
    REEL_DURATION_OPTIONS = [15, 30, 60]  # seconds
    
    # Development Settings
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    @staticmethod
    def init_app(app):
        # Create necessary directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs('frontend/static/reels', exist_ok=True)
        os.makedirs('frontend/static/thumbnails', exist_ok=True)
        os.makedirs('frontend/static/posters', exist_ok=True)

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    DEBUG = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 