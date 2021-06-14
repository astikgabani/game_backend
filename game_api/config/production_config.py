import os

DEBUG = False
ENV = "production"
TESTING = False
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
SECRET_KEY = os.environ["APP_SECRET_KEY"]
