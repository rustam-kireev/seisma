# -*- coding: utf-8 -*-

from http import HTTPStatus as statuses

import flask

from ..utils import cast_to_int
from ..result import make_result
from ..utils import cast_to_float
from ..resource import ApiResource
from ..utils import paginated_query
from ...database import schema as db
from ..utils import string_to_datetime


resource = ApiResource(__name__, version=1)


def _get_build_by_name(name):
    return db.Build.query.filter_by(
        name=name, is_active=True,
    ).first()


@resource.route('/builds', methods=['GET'])
def get_builds():
    query = db.Build.query.filter_by(is_active=True)
    query = paginated_query(query, flask.request)

    return make_result(
        query.all(),
        total_count=query.total_count,
        current_count=query.current_count,
    ), statuses.OK


@resource.route('/builds', methods=['POST'], schema='build.post.json')
def create_build():
    data = {
        'is_active': True,
        'name': flask.request.json.get('name'),
        'description': flask.request.json.get('description'),
    }
    build = db.Build.create(**data)

    return make_result(build), statuses.CREATED


@resource.route('/builds/<string:name>', methods=['GET'])
def get_build_by_name(name):
    build = _get_build_by_name(name)

    if build:
        return make_result(build), statuses.OK


@resource.route('/builds/<string:name>', methods=['DELETE'])
def delete_build_by_name(name):
    build = _get_build_by_name(name)

    if build:
        build.update(is_active=False)
        return make_result(build), statuses.OK


@resource.route('/builds/<string:name>/results', methods=['GET'])
def get_build_results(name):
    build = _get_build_by_name(name)

    if build:
        filters = {
            'build_id': build.id,
        }

        date_to = flask.request.args.get('date_to', None)
        date_from = flask.request.args.get('date_from', None)
        was_success = flask.request.args.get('was_success', None)
        runtime_more = flask.request.args.get('runtime_more', None)
        runtime_less = flask.request.args.get('runtime_less', None)
        fail_count_more = flask.request.args.get('fail_count_more', None)
        fail_count_less = flask.request.args.get('fail_count_less', None)
        error_count_more = flask.request.args.get('error_count_more', None)
        error_count_less = flask.request.args.get('error_count_less', None)
        success_count_more = flask.request.args.get('success_count_more', None)
        success_count_less = flask.request.args.get('success_count_less', None)

        if was_success == 'false':
            filters['was_success'] = False
        elif was_success == 'true':
            filters['was_success'] = True

        query = db.BuildResult.query.filter_by(**filters)

        if date_from is not None:
            date_from = string_to_datetime(date_from, no_time=True)
            query = query.filter(db.BuildResult.date >= date_from)

        if date_to is not None:
            date_to = string_to_datetime(date_to, no_time=True, to_end_day=True)
            query = query.filter(db.BuildResult.date <= date_to)

        if runtime_more is not None:
            query = query.filter(db.BuildResult.runtime > cast_to_float(runtime_more))
        elif runtime_less is not None:
            query = query.filter(db.BuildResult.runtime < cast_to_float(runtime_less))

        if fail_count_more is not None:
            query = query.filter(db.BuildResult.fail_count > cast_to_int(fail_count_more))
        elif fail_count_less is not None:
            query = query.filter(db.BuildResult.fail_count < cast_to_int(fail_count_less))

        if error_count_more is not None:
            query = query.filter(db.BuildResult.error_count > cast_to_int(error_count_more))
        elif error_count_less is not None:
            query = query.filter(db.BuildResult.error_count < cast_to_int(error_count_less))

        if success_count_more is not None:
            query = query.filter(db.BuildResult.success_count > cast_to_int(success_count_more))
        elif success_count_less is not None:
            query = query.filter(db.BuildResult.success_count < cast_to_int(success_count_less))

        query = paginated_query(query, flask.request)

        return make_result(
            query.all(),
            total_count=query.total_count,
            current_count=query.current_count,
            build=build,
        ), statuses.OK


@resource.route('/builds/<string:name>/results', methods=['POST'], schema='build_result.post.json')
def create_build_result(name):
    build = _get_build_by_name(name)

    if build:
        data = {
            'build_id': build.id,
            'name': flask.request.json.get('name'),
            'runtime': 0.0,
            'fail_count': 0,
            'error_count': 0,
            'tests_count': 0,
            'success_count': 0,
            'is_running': True,
            'was_success': False,

        }
        metadata = flask.request.json.get('metadata')

        build_result = db.BuildResult.create(**data)

        if metadata:
            build_result.md = metadata

        return make_result(
            build_result,
            build=build,
        ), statuses.CREATED


@resource.route('/builds/<string:name>/results/<string:result_name>', methods=['PUT'])
def update_build_result(name, result_name):
    build = _get_build_by_name(name)

    if build:
        query = db.BuildResult.query.filter_by(
            build_id=build.id, name=result_name,
        )
        build_result = query.first()

        if build_result:
            data = {
                'is_running': False,
                'runtime': flask.request.json.get('runtime'),
                'was_success': flask.request.json.get('was_success'),
                'tests_count': flask.request.json.get('tests_count'),
                'success_count': flask.request.json.get('success_count'),
                'fail_count': flask.request.json.get('fail_count'),
                'error_count': flask.request.json.get('error_count'),
            }
            build_result.update(**data)

            return make_result(
                build_result,
                build=build,
            ), statuses.OK


@resource.route('/builds/<string:name>/results/<string:result_name>', methods=['GET'])
def get_build_result(name, result_name):
    build = _get_build_by_name(name)

    if build:
        query = db.BuildResult.query.filter_by(
            build_id=build.id, name=result_name,
        )
        build_result = query.first()

        if build_result:
            return make_result(
                build_result,
                build=build,
            ), statuses.OK


@resource.route('/builds/<string:name>/cases/<string:case_name>', methods=['GET'])
def get_case(name, case_name):
    build = _get_build_by_name(name)

    if build:
        case = db.Case.query.filter_by(build_id=build.id, name=case_name).first()

        if case:
            return make_result(
                case,
                build=build,
            ), statuses.OK


@resource.route('/builds/<string:name>/cases', methods=['POST'], schema='case.post.json')
def create_case(name):
    build = _get_build_by_name(name)

    if build:
        data = {
            'build_id': build.id,
            'name': flask.request.json.get('name'),
            'description': flask.request.json.get('description'),
        }
        case = db.Case.create(**data)

        return make_result(
            case,
            build=build,
        ), statuses.CREATED


@resource.route('/builds/<string:name>/cases', methods=['GET'])
def get_cases(name):
    build = _get_build_by_name(name)

    if build:
        query = db.Case.query.filter_by(build_id=build.id)
        query = paginated_query(query, flask.request)

        return make_result(
            query.all(),
            total_count=query.total_count,
            current_count=query.current_count,
            build=build,
        ), statuses.OK


@resource.route('/builds/<string:name>/cases/<string:case_name>/results', methods=['GET'])
def get_case_results(name, case_name):
    build = _get_build_by_name(name)

    if build:
        case = db.Case.query.filter_by(build_id=build.id, name=case_name).first()

        if case:
            query = db.CaseResult.query.filter_by(case_id=case.id)
            query = paginated_query(query, flask.request)

            return make_result(
                query.all(),
                total_count=query.total_count,
                current_count=query.current_count,
                build=build,
                case=case,
            ), statuses.OK


@resource.route(
    '/builds/<string:name>/results/<string:result_name>/cases/<string:case_name>',
    methods=['POST'],
    schema='case_result.post.json',
)
def create_case_result(name, result_name, case_name):
    build = _get_build_by_name(name)

    if build:
        build_result = db.BuildResult.query.filter_by(build_id=build.id, name=result_name).first()

        if build_result:
            case = db.Case.query.filter_by(build_id=build.id, name=case_name).first()

            if case:
                data = {
                    'case_id': case.id,
                    'build_result_id': build_result.id,
                    'status': flask.request.json.get('status'),
                    'runtime': flask.request.json.get('runtime'),
                    'reason': flask.request.json.get('reason', ''),
                }
                metadata = flask.request.json.get('metadata')

                case_result = db.CaseResult.create(**data)

                if metadata:
                    case_result.md = metadata

                return make_result(
                    case_result,
                    build_result=build_result,
                    build=build,
                    case=case,
                ), statuses.CREATED


@resource.route(
    '/builds/<string:name>/results/<string:result_name>/cases/<string:case_name>',
    methods=['GET'],
)
def get_case_result(name, result_name, case_name):
    build = _get_build_by_name(name)

    if build:
        build_result = db.BuildResult.query.filter_by(build_id=build.id, name=result_name).first()

        if build_result:
            case = db.Case.query.filter_by(build_id=build.id, name=case_name).first()

            if case:
                case_result = db.CaseResult.query.filter_by(
                    build_result_id=build_result.id, case_id=case.id,
                ).first()

                if case_result:
                    return make_result(
                        case_result,
                        build_result=build_result,
                        build=build,
                        case=case,
                    ), statuses.OK


@resource.route('/builds/<string:name>/cases/results')
def get_all_case_results_from_build(name):
    build = _get_build_by_name(name)

    if build:
        status = flask.request.args.get('status', None)
        date_to = flask.request.args.get('date_to', None)
        date_from = flask.request.args.get('date_from', None)
        runtime_more = flask.request.args.get('runtime_more', None)
        runtime_less = flask.request.args.get('runtime_less', None)

        query = db.CaseResult.query.join(
            db.BuildResult,
        ).filter(db.BuildResult.build_id == build.id)

        if date_from is not None:
            date_from = string_to_datetime(date_from, no_time=True)
            query = query.filter(db.CaseResult.date >= date_from)

        if date_to is not None:
            date_to = string_to_datetime(date_to, no_time=True, to_end_day=True)
            query = query.filter(db.CaseResult.date <= date_to)

        if status in ('passed', 'skipped', 'failed', 'error'):
            query = query.filter(db.CaseResult.status == status)

        if runtime_more is not None:
            query = query.filter(db.CaseResult.runtime > cast_to_float(runtime_more))
        elif runtime_less is not None:
            query = query.filter(db.CaseResult.runtime < cast_to_float(runtime_less))

        query = paginated_query(query, flask.request)

        return make_result(
            query.all(),
            total_count=query.total_count,
            current_count=query.current_count,
            build=build,
        ), statuses.OK
