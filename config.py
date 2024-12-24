import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret-key')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/secure_file_storage')
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET', 'your-bucket-name')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'your-access-key-id')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'your-secret-access-key')
