# -*- coding: utf-8 -*-
from .base import *
import os
import environ

env = environ.Env()
env.read_env('/opt/app/cecile/.env')

DEBUG = False
IS_PERFORMANCE_TEST = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

INTERNAL_IPS = ('127.0.0.1', 'localhost')

MIDDLEWARE += (
   'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS += (
    'reversion',
)


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    },
}


# Loggins configure
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(process)d] [%(asctime)s] %(levelname)s [%(filename)s:%(lineno)s] %(message)s'
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*1024,
            'backupCount': 5,
            'filename': '/tmp/run.log',
            'formatter': 'verbose'
        },
        'web_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*1024*100,
            'backupCount': 5,
            'filename': env('WEB_ERROR_LOG_PATH'),
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'logs': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'web': {
            'handlers': ['web_file'],
            'level': 'DEBUG',
        }
    },
}

STATIC_URL = '/static/'
MEDIA_URL = '/static/media/'
MEDIA_ROOT = '/opt/app/cecile/data/media/'