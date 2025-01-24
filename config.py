import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost:8111/capstone2'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "jwt_secret_key"
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'elcapstone69@gmail.com'
    MAIL_PASSWORD = 'siad fffv ajwx zsly'
    MAIL_DEFAULT_SENDER = 'elcapstone69@gmail.com'
    BASE_URL = 'http://localhost:5000'
    OTP_EXPIRY_MINUTES = 10

class ProductionConfig(Config):
    BASE_URL = 'https://yourproductiondomain.com'  # URL produksi

class DevelopmentConfig(Config):
    DEBUG = True