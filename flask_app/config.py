import os

class Config:
    Debug = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = "image_pool"
    
class DevelopmentConfig(Config):
    Debug = True
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
    FLASK_ENV = "development"
    
    
class StagingConfig(Config):
    Debug = True
    SECRET_KEY = os.getenv("SECRET_KEY", "staging-key")
    FLASK_ENV = "staging"

class ProductionConfig(Config):
    SECRET_KEY = 'prod-key'
    FLASK_ENV = "production"