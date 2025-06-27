#backend/config/settings.py
import os
import dj_database_url
from pathlib import Path

# === BASE DIRECTORY ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === CONFIG URL ===
ROOT_URLCONF = "config.urls"
# === SECURITY KEYS ===
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-key")

DEBUG = False

ALLOWED_HOSTS = [
    "frontend-dixafaq-production-853e.up.railway.app",
    "backend-dixafaq-production.up.railway.app"
]
 
CSRF_TRUSTED_ORIGINS = ["https://frontend-dixafaq-production-853e.up.railway.app","https://backend-dixafaq-production.up.railway.app"]  

# === API Keys ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DIXA_API_TOKEN = os.getenv("DIXA_API_TOKEN", "")
ELEVIO_API_KEY = os.getenv("ELEVIO_API_KEY", "")
ELEVIO_JWT = os.getenv("ELEVIO_JWT", "")

# === LOGIN Urls ===
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = '/dashboard/' 

# === DATABASE ===
DATABASES = {
    "default": dj_database_url.config(conn_max_age=600)
}
# === TEMPLATES ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# === CELERY CONFIGURATION ===
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_BACKEND = None  
CELERY_TIMEZONE = "Europe/Amsterdam" 
USE_TZ = True
TIME_ZONE = "Europe/Amsterdam"
CELERY_ENABLE_UTC = False 
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# === APPLICATIONS ===
INSTALLED_APPS = [
    "faq_api",
    "rest_framework",
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_beat",
]

# === WSGI ===
WSGI_APPLICATION = "config.wsgi.application"

# === MIDDLEWARE ===
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# === CORS CONFIG ===
CORS_ALLOW_CREDENTIALS = True  
CORS_ALLOWED_ORIGINS = [
    "https://frontend-dixafaq-production-853e.up.railway.app",
]

# === CSRF CONFIG ===
CSRF_TRUSTED_ORIGINS = [
    "https://frontend-dixafaq-production-853e.up.railway.app",
    "https://backend-dixafaq-production.up.railway.app",
]

SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True

# === STATIC FILES ===
STATIC_URL = "static/"

# === REST FRAMEWORK SETTINGS ===
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ]
}
# === DEFAULT ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
