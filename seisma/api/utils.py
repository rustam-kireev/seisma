# -*- coding: utf-8 -*-

import datetime

from .. import json
from .. import exceptions


DEFAULT_RECORDS_ON_PAGE = 100


def paginated_query(query, request):
    query.total_count = query.count()

    from_ = request.args.get('from', 1)
    to_ = request.args.get('to', DEFAULT_RECORDS_ON_PAGE)

    query = query.slice(int(from_) - 1, int(to_))

    query.current_count = query.count()

    return query


def string_to_datetime(string, no_time=False, to_end_day=False):
    try:
        dt = datetime.datetime.strptime(
            string, json.DATE_FORMAT if no_time else json.DATETIME_FORMAT,
        )
    except ValueError as error:
        raise exceptions.ValidationError(*error.args)

    if to_end_day:
        return datetime.datetime(
            dt.year,
            dt.month,
            dt.day,
            minute=59,
            hour=23,
            second=59,
            microsecond=999999,
        )

    return dt


def cast_to_float(value):
    try:
        return float(value)
    except ValueError:
        raise exceptions.ValidationError('"{}" is not a float'.format(value))


def cast_to_int(value):
    try:
        return int(value)
    except ValueError:
        raise exceptions.ValidationError('"{}" is not a integer'.format(value))
