from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*']

CORS_ALLOWED_ORIGINS = ['http://localhost:8000']

CSRF_TRUSTED_ORIGINS = ['http://localhost:8000']

WSGI_APPLICATION = 'server.wsgi.deploy.application'

# Celery
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'