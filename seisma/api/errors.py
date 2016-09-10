# -*- coding: utf-8 -*-

import logging

import flask
from sqlalchemy.exc import IntegrityError

from .. import json
from . import result
from .. import exceptions


logger = logging.getLogger(__name__)


EXCEPTION_CLASS_TO_STATUS_CODE = (
    (exceptions.ValidationError, 400),
    (IntegrityError, 409),
    (exceptions.NotFound, 404),
    (exceptions.BaseSeismaException, 500),
    (Exception, 500),
)


def error_handler(status_code):
    """
    Общий обработчик исключений приложения.
    """
    def wrapper(exc):
        if status_code in (500, 400):
            logger.error(exc, exc_info=True)
        else:
            logger.debug(exc, exc_info=True)

        rv = result.make_error_result(exc.args, exc=exc)

        return flask.Response(
            json.dumps(rv),
            status=status_code,
            mimetype=json.JSON_MIME_TYPE,
        )
    return wrapper
