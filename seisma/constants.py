# -*- coding: utf-8 -*-

import os


TESTING_MODE = os.getenv('SEISMA_TESTING', False)

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
            'test_config.py',
        ),
    )
    MIGRATE_DIR = TEST_MIGRATE_DIR
else:
    DEFAULT_CONFIG = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            'default_config.py',
        ),
    )
    MIGRATE_DIR = PRODUCTION_MIGRATE_DIR


os.environ.setdefault(CONFIG_ENV_NAME, DEFAULT_CONFIG)
