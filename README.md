# 🚀 DRF Baseline

**DRF Baseline** is a Django REST Framework boilerplate that helps you quickly set up a clean, scalable backend for your next project.  
It supports `.env` configuration, JWT authentication, CORS setup, static file handling, and production-ready deployment structure.

---

## 📦 Features

- ✅ Django REST Framework
- 🔐 JWT Authentication (SimpleJWT)
- ⚙️ Environment-based settings (`dev` / `deploy`)
- 🌐 CORS support
- 📁 Static file configuration
- 🐳 Dockerfile included

---

## 📌 Getting Started

1. **Clone the project**
   ```bash
   git clone https://github.com/your-username/drf_baseline.git
   ```
2. **Add a '.env' file in '/server'**.
   ```env
   SECRET_KEY='your_secret_key'
   ```
3. **(Optional)** Collect static files.
   ```bash
   python manage.py collectstatic
   ```
4. **Install dependencies**
   Make sure to use a virtual environment:
   ```bash
   pip install -r requirements.txt
   ```
5. **Apply migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
6. **Run development server**
   ```bash
   python manage.py runserver
   ```
7. **Run deployment server**
   ```bash
   python manage.py runserver --settings=server.settings.deploy
   ```

---

## 🗂 Project Structure

```text
├── server
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
│   ├── .env
│   └── urls.py
├── .gitignore
├── Dockerfile
├── requirements.txt
├── README.md
└── manage.py
```

---

## 🛠️ Configuration Details

### 📄 manage.py
```python
default environment : server.settings.dev
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings.dev')
```

---

### ⚙️ server/settings/base.py

1. **dotenv**
```env
import os, dotenv
dotenv.load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
```

2. **JWT**
```python
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
```

3. **CORS**
```python
INSTALLED_APPS = ['corsheaders']
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware']
```

4. **Static files**
```python
import os
STATIC_ROOT = os.path.join(BASE_DIR, "static")
run '$ python manage.py collectstatic'
```

---

### 🧪 server/settings/dev.py

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True
WSGI_APPLICATION = 'appserver.wsgi.dev.application'
```

---

### 🚀 server/settings/deploy.py

```python
DEBUG = False
ALLOWED_HOSTS = ['*']
CORS_ALLOWED_ORIGINS = ['http://localhost:8000']
WSGI_APPLICATION = 'appserver.wsgi.deploy.application'
```