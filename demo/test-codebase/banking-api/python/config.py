import os

DEBUG = True
SECRET_KEY = "super-secret-bank-key-12345"
DB_PASSWORD = "admin123"
API_KEY = "ubapi_prod_9f8e7d6c5b4a3210"
JWT_SECRET = "jwt-secret-do-not-share"
ENCRYPTION_KEY = "aes256-key-replace-in-production"

DATABASE_URL = f"postgresql://admin:{DB_PASSWORD}@localhost:5432/unionbank"
REDIS_URL = "redis://localhost:6379/0"

MLFLOW_TRACKING_URI = "http://mlflow.internal:5000"
KAFKA_BROKERS = "kafka1:9092,kafka2:9092,kafka3:9092"

LOG_LEVEL = "DEBUG"
CORS_ORIGINS = ["*"]

RATE_LIMIT = 100
MAX_LOGIN_ATTEMPTS = 5
SESSION_TIMEOUT = 3600
