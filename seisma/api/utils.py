# -*- coding: utf-8 -*-

from urllib.parse import quote


DEFAULT_RECORDS_ON_PAGE = 100


def paginated_query(query, request):
    query.total_count = query.count()

    from_ = request.args.get('from', 1)
    to_ = request.args.get('to', DEFAULT_RECORDS_ON_PAGE)

    query = query.slice(int(from_) - 1, int(to_))

    query.current_count = query.count()

    return query


def api_location(path, *args, **kwargs):
    version = kwargs['version']

    return '/api/v{}{}'.format(
        version,
        path.format(*[quote(a) for a in args]),
    )
