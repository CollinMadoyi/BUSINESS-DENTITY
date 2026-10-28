import os

os.environ.setdefault('SECRET_KEY', 'test-only-secret-key')
os.environ.setdefault('DATABASE_URL', 'postgresql://test:test@localhost/test')

from .settings import *

SECRET_KEY = 'test-only-secret-key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}
