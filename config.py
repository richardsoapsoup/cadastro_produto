import os

class Config:
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:123456@localhost/aplicativo_flask')

