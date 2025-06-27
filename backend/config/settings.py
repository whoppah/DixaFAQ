#backend/config/settings.py
import os
import dj_database_url
from pathlib import Path

# === BASE DIRECTORY ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === SECURITY ===
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-key")
DEBUG = False

# Production URLs allowed to access backend
ALLOWED_HOSTS = [
    "https://frontend-dixafaq-production-853e.up.railway.app",
    "https://backend-dixafaq-production.up.railway.app",
]

# CSRF protection for trusted origins
CSRF_TRUSTED_ORIGINS = [
    "https://frontend-dixafaq-production-853e.up.railway.app",
    "https://backend-dixafaq-production.up.railway.app",
]

# === DATABASE ===
DATABASES = {
    "default": dj_database_url.config(conn_max_age=600)
}

# === INSTALLED APPS ===
INSTALLED_APPS = [
    "faq_api",
    "rest_framework",
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django_celery_beat",
    'django.contrib.auth',         # Removed: not using login
    'django.contrib.sessions',     # Removed: not using sessions
    'django.contrib.messages',     # Removed: not using messaging framework
]

# === MIDDLEWARE ===
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # "django.contrib.sessions.middleware.SessionMiddleware",  # Not needed without sessions
    # "django.contrib.auth.middleware.AuthenticationMiddleware",  # Not needed without auth
    # "django.contrib.messages.middleware.MessageMiddleware",     # Not needed
]

# === CORS CONFIG ===
CORS_ALLOW_CREDENTIALS = False  # No login session/cookies needed
CORS_ALLOWED_ORIGINS = [
    "https://frontend-dixafaq-production-853e.up.railway.app",
    "https://backend-dixafaq-production.up.railway.app",
]

# === CSRF COOKIES ===
CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True

# === STATIC FILES ===
STATIC_URL = "static/"

# === REST FRAMEWORK SETTINGS ===
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    # "DEFAULT_PERMISSION_CLASSES": [],  # Optional: could explicitly allow unrestricted access
}

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
            ],
        },
    },
]

# === WSGI ===
WSGI_APPLICATION = "config.wsgi.application"

# === AUTO FIELD ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
