# -*- coding: utf-8 -*-

import logging

from sqlalchemy.exc import InvalidRequestError
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy

from .. import exceptions


logger = logging.getLogger(__name__)


DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 3306
DEFAULT_USER = 'root'
DEFAULT_PASSWORD = ''
DEFAULT_DB_NAME = 'seisma'

DEFAULT_POOL_SIZE = 5
DEFAULT_POOL_TIMEOUT = 10
DEFAULT_POOL_RECYCLE = 60 * 5
DEFAULT_MAX_OVERFLOW = -1
DEFAULT_SQL_LOG = False
DEFAULT_TRACK_MODIFICATIONS = False


alchemy = None
session = None


def setup_uri(app, use_db_name=True):
    config = app.config.get('DATABASE', {})

    host = config.get('HOST', DEFAULT_HOST)
    port = config.get('PORT', DEFAULT_PORT)

    user = config.get('USER', DEFAULT_USER)
    password = config.get('PASSWORD', DEFAULT_PASSWORD)

    database = config.get('NAME', DEFAULT_DB_NAME)

    uri = 'mysql+mysqlconnector://{user}:{password}@{host}:{port}/'.format(
        user=user,
        password=password,
        host=host,
        port=port,
    )

    if use_db_name:
        uri += database
        uri += '?charset=utf8&use_unicode=1'

    app.config['SQLALCHEMY_DATABASE_URI'] = uri


def setup_settings(app):
    config = app.config.get('DATABASE', {})

    app.config['SQLALCHEMY_ECHO'] = config.get('SQL_LOG', DEFAULT_SQL_LOG)
    app.config['SQLALCHEMY_POOL_SIZE'] = config.get('POOL_SIZE', DEFAULT_POOL_SIZE)
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = config.get('POOL_TIMEOUT', DEFAULT_POOL_TIMEOUT)
    app.config['SQLALCHEMY_POOL_RECYCLE'] = config.get('POOL_RECYCLE', DEFAULT_POOL_RECYCLE)
    app.config['SQLALCHEMY_MAX_OVERFLOW'] =config.get('MAX_OVERFLOW', DEFAULT_MAX_OVERFLOW)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.get('TRACK_MODIFICATIONS', DEFAULT_TRACK_MODIFICATIONS)


def setup(app):
    global alchemy, session

    if alchemy is None:
        setup_uri(app, use_db_name=False)
        setup_settings(app)

        alchemy = _SQLAlchemy(app)
        session = alchemy.session

        create_database_if_not_exists(app.config)
        setup_uri(app, use_db_name=True)
    else:
        raise RuntimeError('Database already initialized')


def create_database_if_not_exists(config):
    config = config.get('DATABASE', {})
    db_name = config.get('NAME', DEFAULT_DB_NAME)

    conn = alchemy.engine.connect()
    conn.execute(
        'CREATE DATABASE IF NOT EXISTS {} '
        'DEFAULT CHARACTER SET utf8 '
        'DEFAULT COLLATE utf8_general_ci'.format(db_name),
    )
    conn.close()


def get_connection():
    return alchemy.engine.connect()


class ModelMixin(object):

    __table_args__ = {
        'mysql_engine': 'InnoDB',
    }

    @classmethod
    def create(cls, **params):
        try:
            instance = cls(**params)
        except TypeError as error:
            raise exceptions.ValidationError(
                getattr(error, 'message', None) or ' '.join(error.args),
            )

        alchemy.session.add(instance)
        alchemy.session.commit()

        try:
            alchemy.session.refresh(instance)
        except InvalidRequestError as error:
            logger.warn(error, exc_info=True)

        return instance

    def update(self, **params):
        for k, v in params.items():
            setattr(self, k, v)

        alchemy.session.add(self)
        alchemy.session.commit()

        try:
            alchemy.session.refresh(self)
        except InvalidRequestError as error:
            logger.warn(error, exc_info=True)

    def refresh(self):
        pk_columns = self.__table__.primary_key.columns.keys()
        refreshed_obj = self.query.filter_by(**dict((n, getattr(self, n)) for n in pk_columns))
        data_to_update = dict((k, v) for k, v in refreshed_obj.to_dict().items() if k not in pk_columns)

        for k, v in data_to_update.items():
            setattr(self, k, v)

    def to_dict(self):
        raise NotImplementedError(
            '"to_dict" method does not implemented on "{}"'.format(self.__class__.__name__),
        )
