# -*- coding: utf-8 -*-

import os
import logging
from functools import wraps

import flask
import jsonschema

from .. import json
from . import errors
from . import response
from .. import exceptions


logger = logging.getLogger(__name__)


BASE_API_PATH_INFO = '/api'
DEFAULT_RESOURCE_VERSION = 1

SCHEMAS_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        'schemas',
    ),
)


def validate_inputs_decorator(f, schema):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            jsonschema.validate(flask.request.json, schema)
        except jsonschema.ValidationError as error:
            raise exceptions.ValidationError(*[e for e in error.args if isinstance(e, str)])
        return f(*args, **kwargs)
    return wrapper


def not_found_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        if result is None:
            raise exceptions.NotFound('Object is not found')
        return result
    return wrapper


def response_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return response.make_response(
            f(*args, **kwargs),
        )
    return wrapper


def decorate_view(f, schema=None):
    @wraps(f)
    def wrapper(view):
        view = not_found_decorator(view)

        if schema is not None:
            view = validate_inputs_decorator(
                view, schema,
            )

        view = response_decorator(view)

        return f(view)
    return wrapper


class ApiResource(flask.Blueprint):

    def __init__(self, name, *args, **kwargs):
        kwargs.update(import_name=name)

        self.version = kwargs.pop('version', DEFAULT_RESOURCE_VERSION)

        super(ApiResource, self).__init__(name, *args, **kwargs)

        self.setup_error_handlers()

    def route(self, rule, **options):
        version = options.pop('version', None) or self.version
        rule = '{}/v{}{}'.format(BASE_API_PATH_INFO, version, rule)

        schema = options.pop('schema', None)

        if schema:
            schema_path = os.path.join(SCHEMAS_PATH, 'v{}'.format(version), schema)

            with open(schema_path) as fp:
                schema = json.load(fp)

        return decorate_view(
            super(ApiResource, self).route(rule, **options),
            schema=schema,
        )

    def setup_error_handlers(self):
        for exception_class, code in errors.EXCEPTION_CLASS_TO_STATUS_CODE:
            self.register_error_handler(exception_class, errors.error_handler(code))
