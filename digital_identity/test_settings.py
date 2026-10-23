import os

# The base settings require a database URL; tests replace this placeholder below.
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
