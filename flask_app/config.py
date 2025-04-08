import os

class Config:
    Debug = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = "image_pool"
    
class DevelopmentConfig(Config):
    Debug = True
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
    
    
class StagingConfig(Config):
    Debug = True
    SECRET_KEY = os.getenv("SECRET_KEY", "staging-key")

class ProductionConfig(Config):
    SECRET_KEY = 'prod-key'