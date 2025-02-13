from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ALLOW_ALL_ORIGINS = True

WSGI_APPLICATION = 'server.wsgi.dev.application'
