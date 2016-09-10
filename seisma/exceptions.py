# -*- coding: utf-8 -*-


class BaseSeismaException(Exception):
    pass


class ValidationError(BaseSeismaException):
    pass


class NotFound(BaseSeismaException):
    pass
