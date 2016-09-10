# -*- coding: utf-8 -*-


def make_result(data, **extra):
    return {
        'result': data,
        'extra': extra,
    }


def make_error_result(messages, type=None, exc=None):
    if exc:
        type = exc.__class__.__name__
    elif not type and not exc:
        type = 'UnknownType'

    if isinstance(messages, str):
        messages = [messages]

    return {
        'type': type,
        'messages': messages,
    }
