import os
from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env_file = BASE_DIR / '.env'
if not env_file.exists():
    env_file = BASE_DIR / '.env.local'
environ.Env.read_env(env_file)

DEBUG = env.bool('DEBUG', default=False)
SECRET_KEY = env('SECRET_KEY', default='')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'local-development-only-insecure-key'
    else:
        raise ImproperlyConfigured('SECRET_KEY must be set when DEBUG is False.')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', 'testserver'])
render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if render_hostname:
    ALLOWED_HOSTS.append(render_hostname)


def default_site_url(debug, hostname):
    if hostname:
        return f'https://{hostname}'
    if debug:
        return 'http://127.0.0.1:8000'
    return ''

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
if render_hostname:
    CSRF_TRUSTED_ORIGINS.append(f'https://{render_hostname}')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'accounts',
    'organizations',
    'profiles',
    'students',
    'companies',
    'portfolio',
    'qrcode_manager',
    'contacts',
    'dashboard',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'digital_identity.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'digital_identity.wsgi.application'

if os.environ.get('NEON_USE_UNPOOLED_DATABASE_URL') == '1':
    database_url = env('DATABASE_URL_UNPOOLED', default='').strip()
    database_url_name = 'DATABASE_URL_UNPOOLED'
else:
    database_url = env('DATABASE_URL', default='').strip()
    database_url_name = 'DATABASE_URL'

if not database_url:
    raise ImproperlyConfigured(f'{database_url_name} must be set to use PostgreSQL.')

DATABASES = {'default': env.db(database_url_name)}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
SITE_URL = env('SITE_URL', default=default_site_url(DEBUG, render_hostname)).rstrip('/')

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

if env.bool('USE_NEON_OBJECT_STORAGE', default=False):
    STORAGES['default'] = {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'bucket_name': env('AWS_STORAGE_BUCKET_NAME'),
            'endpoint_url': env('AWS_ENDPOINT_URL_S3'),
            'region_name': env('AWS_REGION'),
            'access_key': env('AWS_ACCESS_KEY_ID'),
            'secret_key': env('AWS_SECRET_ACCESS_KEY'),
            'addressing_style': 'path',
            'signature_version': 's3v4',
            'querystring_auth': True,
            'file_overwrite': False,
        },
    }

AUTH_USER_MODEL = 'accounts.CustomUser'

LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/admin/login/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
