import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://MySystem:chen526@localhost/MySystem'
    SQLALCHEMY_TRACK_MODIFICATIONS = False