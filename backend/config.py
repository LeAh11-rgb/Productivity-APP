# This file manages app configurations for different environments - class approach so we can have separate configs for development and productivity 

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES_HOURS = 24
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'productivitypro.db')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://127.0.0.1:5500')

class DevelopmentCongfig (Config):
    DEBUG = True
    TESTING = False

class ProductionConfig (Config):
    DEBUG = False
    TESTING = False

config_map = {
    'development': DevelopmentCongfig, 
    'production': ProductionConfig, 
    'default': DevelopmentCongfig
}