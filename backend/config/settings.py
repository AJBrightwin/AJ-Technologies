"""
Django settings for the AJ Technologies website (config project).

Database : Supabase PostgreSQL (DATABASE_URL in backend/.env).
           Tables are created by supabase_schema.sql and shared with the admin dashboard project.
Images   : uploaded by the admin dashboard to the Supabase Storage bucket; the website only shows them.

https://docs.djangoproject.com/en/6.1/topics/settings/
"""

import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL, SUPABASE_URL from backend/.env
load_dotenv(BASE_DIR / '.env', encoding='utf-8-sig')


def env(name, default=''):
    return os.getenv(name, default).strip()


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', 'development-only-key-change-me')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = [h.strip() for h in env('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',') if h.strip()]

# Full addresses the quote forms are posted from, e.g. https://ajtechnologiesltd.com
CSRF_TRUSTED_ORIGINS = [o.strip() for o in env('CSRF_TRUSTED_ORIGINS').split(',') if o.strip()]


# Application definition

# Only what the public website needs. No Django admin, login or session tables are created in Supabase.
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'main',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',      # serves CSS/images when the site is live
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',      # protects the quote forms
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database: Supabase PostgreSQL
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASE_URL = env('DATABASE_URL')
if not DATABASE_URL:
    raise ImproperlyConfigured(
        'DATABASE_URL is missing. Add your Supabase connection string to backend/.env, e.g. '
        'DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.YOUR-REF.supabase.co:5432/postgres'
    )

DATABASES = {
    'default': dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=60,          # reuse connections for 60 seconds
        conn_health_checks=True,  # reconnect automatically if Supabase closed the connection
        ssl_require=env('DATABASE_SSL', 'true').lower() == 'true',  # Supabase requires SSL
    )
}


# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Static files (CSS, JavaScript, site images)

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']      # backend/static/images/...
STATIC_ROOT = BASE_DIR / 'staticfiles'        # filled by "python manage.py collectstatic" when you deploy

# Live site: compressed files with long browser caching (needs collectstatic).
# On your laptop (DEBUG=True) Django serves the files as usual.
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage' if DEBUG
        else 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}


# Project images: Supabase Storage (uploaded by the admin dashboard)
# Image links are built as: SUPABASE_URL/storage/v1/object/public/<bucket>/<image_path>

SUPABASE_URL = env('SUPABASE_URL')                                   # e.g. https://abcd1234.supabase.co
SUPABASE_STORAGE_BUCKET = env('SUPABASE_STORAGE_BUCKET', 'project-images')


# Security for the live site (switched on automatically when DEBUG=False)

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')   # hosting provider handles HTTPS
    SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT', 'true').lower() == 'true'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(env('SECURE_HSTS_SECONDS', '3600'))    # raise to 31536000 once HTTPS works well
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'


# Logging: errors are printed to the server log so you can see what went wrong

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'WARNING'},
    'loggers': {'main': {'handlers': ['console'], 'level': 'INFO', 'propagate': False}},
}



# Email: not used yet. Added later for the new-enquiry alerts and thank-you emails.