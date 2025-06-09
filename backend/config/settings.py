#backend/config/settings.py
import os
import dj_database_url
from pathlib import Path

# === BASE DIRECTORY ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === SECURITY KEYS ===
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-key")

DEBUG = False

ALLOWED_HOSTS = ["*"]  # For dev/testing; tighten in prod
CSRF_TRUSTED_ORIGINS = ["*"] # For dev/testing; tighten in prod

# === API Keys ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DIXA_API_TOKEN = os.getenv("DIXA_API_TOKEN", "")
ELEVIO_API_KEY = os.getenv("ELEVIO_API_KEY", "")
ELEVIO_JWT = os.getenv("ELEVIO_JWT", "")

# === DATABASE ===
DATABASES = {
    "default": dj_database_url.config(conn_max_age=600)
}

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
]

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
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",                  
    "https://<your-app>.up.railway.app",       # Railway frontend
]

# === STATIC FILES ===
STATIC_URL = "static/"

# === REST FRAMEWORK SETTINGS ===
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ]
}
