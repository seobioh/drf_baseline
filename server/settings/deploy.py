from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*']

CORS_ALLOWED_ORIGINS = ['http://localhost:8000']

WSGI_APPLICATION = 'server.wsgi.deploy.application'
