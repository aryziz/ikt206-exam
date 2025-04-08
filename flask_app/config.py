import os

SECRET_KEY = "fdsafasd"
UPLOAD_FOLDER = "image_pool"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
DEBUG = True

class Config:
    Debug = False
    
class DevelopmentConfig(Config):
    Debug = True
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")

class ProductionConfig(Config):
    SECRET_KEY = 'prod-key'