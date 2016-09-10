# -*- coding: utf-8 -*-

import logging
from enum import Enum

import flask

from .. import json


logger = logging.getLogger(__name__)


DEFAULT_STATUS_CODE = 200


def is_status(code):
    return (
        type(code) is int
        or
        isinstance(code, Enum)
    )


def make_response(rv):
    status_or_headers = headers = None

    if isinstance(rv, tuple):
        rv, status_or_headers, headers = rv + (None,) * (3 - len(rv))

    if is_status(status_or_headers):
        status_code = status_or_headers
    elif isinstance(status_or_headers, dict) and is_status(headers):
        status_code = headers
        headers = status_or_headers
    elif isinstance(status_or_headers, dict) and headers is None:
        headers = status_or_headers
        status_code = DEFAULT_STATUS_CODE
    else:
        status_code = DEFAULT_STATUS_CODE

    return flask.Response(
        json.dumps(rv),
        headers=headers,
        status=status_code,
        mimetype=json.JSON_MIME_TYPE,
    )