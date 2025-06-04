import os
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}

DEBUG = False
ALLOWED_HOSTS = ['*']  # for testing; restrict in production
CSRF_TRUSTED_ORIGINS = ['https://<your-app>.up.railway.app']

# Secret keys from env
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-key")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DIXA_API_TOKEN = os.getenv("DIXA_API_TOKEN", "")
ELEVIO_API_KEY = os.getenv("ELEVIO_API_KEY", "")
ELEVIO_JWT = os.getenv("ELEVIO_JWT", "")
