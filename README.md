# DRF Baseline

**DRF Baseline** is a Django REST Framework (DRF) boilerplate designed to help you quickly set up and start a new DRF project.  
It provides a structured environment with separate configurations for **development** and **deployment**, ensuring a smooth transition from local testing to production.

It includes pre-configured dotenv, JWT, CORS, static files and Dockerfile.


## 📌 How to Use

1. clone current project.
2. add '.env' file on '/server'.
3. add SECRET_KEY = 'your_secret_key'.
4. (optional) run '$ python manage.py collectstatic' for static file collection.
5. install dependencies writen on Dockerfile.
6. run 'python manage.py runserver' for development server.
7. run 'python manage.py runserver --settings=server.settings.deploy' for deployment server.


## 📌 DRF Baseline Structure

├──server
│   ├── .env
│   ├── settings
│   │   ├── base.py
│   │   ├── deploy.py
│   │   └── dev.py
│   ├── wsgi
│   │   ├── deploy.py
│   │   └── dev.py
│   ├── asgi.py
│   ├── static
│   ├── db.sqlite3
│   └── urls.py
├── .gitignore
├── Dockerfile
├── README.md
└── manage.py


## 📌 DRF Baseline Detail

### manage.py

default environment : server.settings.dev
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings.dev')


### server/settings/base.py

1. dotenv
import os, dotenv
dotenv.load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')


2. JWT
from datetime import timedelta
INSTALLED_APPS = ['rest_framework_simplejwt']
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication')     # JWT
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


3. CORS
INSTALLED_APPS = ['corsheaders']
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware']


4. Static files
import os
STATIC_ROOT = os.path.join(BASE_DIR, "static")
run '$ python manage.py collectstatic'



### server/settings/dev.py

DEBUG = True
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True
WSGI_APPLICATION = 'appserver.wsgi.dev.application'



### server/settings/deploy.py

DEBUG = False
ALLOWED_HOSTS = ['*']
CORS_ALLOWED_ORIGINS = ['http://localhost:8000']
WSGI_APPLICATION = 'appserver.wsgi.deploy.application'
