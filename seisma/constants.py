# -*- coding: utf-8 -*-

import os


TESTING_MODE = bool(os.getenv('SEISMA_TESTING', False))

USER_HOME = os.path.expanduser('~')

SEISMA_DATA_DIR = os.path.join(
    USER_HOME, '.seisma',
)

MIGRATE_DIR = os.path.join(
    SEISMA_DATA_DIR, 'migrations',
)

PRODUCTION_MIGRATE_DIR = os.path.join(
    MIGRATE_DIR, 'production',
)

TEST_MIGRATE_DIR = os.path.join(
    MIGRATE_DIR, 'test',
)


if not os.path.exists(SEISMA_DATA_DIR):
    os.mkdir(SEISMA_DATA_DIR)

if not os.path.exists(MIGRATE_DIR):
    os.mkdir(MIGRATE_DIR)


CONFIG_ENV_NAME = 'SEISMA_SETTINGS'


if TESTING_MODE:
    DEFAULT_CONFIG = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            'conf', 'test.py',
        ),
    )
    MIGRATE_DIR = TEST_MIGRATE_DIR
else:
    DEFAULT_CONFIG = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            'conf', 'default.py',
        ),
    )
    MIGRATE_DIR = PRODUCTION_MIGRATE_DIR


os.environ.setdefault(CONFIG_ENV_NAME, DEFAULT_CONFIG)


API_AUTO_CREATION_PARAM = 'autocreation'
