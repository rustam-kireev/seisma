# -*- coding: utf-8 -*-

import sys


# Application settings

DEBUG = False
TESTING = False


# Database settings

DATABASE = {
    'HOST': 'localhost',
    'PORT': 3306,
    'USER': 'root',
    'PASSWORD': '',
    'NAME': 'seisma',
    'POOL_SIZE': 10,
    'POOL_TIMEOUT': 10,
    'POOL_RECYCLE': 60 * 5,
    'MAX_OVERFLOW': -1,
    'SQL_LOG': False,
    'TRACK_MODIFICATIONS': False,
}


# Logging settings

LOGGING_SETTINGS = {
    'version': 1,
    'formatters': {
        'basic': {
            'format': '%(asctime)-15s %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'stream': sys.stderr,
            'formatter': 'basic'
        },
        'null': {
            'class': 'logging.NullHandler',
            'level': 'DEBUG'
        },
    },
    'loggers': {
        'seisma': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'flask': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'flask_sqlalchemy': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'flask_migrate': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'flask_script': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'sqlalchemy': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    'root': {
        'propagate': False,
        'handlers': ['console'],
        'level': 'INFO',
    },
}
