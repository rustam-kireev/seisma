# -*- coding: utf-8 -*-

from http import HTTPStatus as statuses

import flask

from .. import string
from ..result import make_result
from ..utils import api_location
from ..resource import ApiResource
from ..utils import paginated_query
from ...database import schema as db
from ...constants import API_AUTO_CREATION_PARAM


VERSION = 1


resource = ApiResource(__name__, version=VERSION)


@resource.route('/jobs/<string:job_name>/builds', methods=['GET'])
def get_builds_from_job(job_name):
    """
    Get builds from job.

    METHOD: GET
    PATH: /api/v1/jobs/<string:job_name>/builds

    GET params

        * date_to: where data less or equal than value.
        * date_from: where data more or equal than value.
        * runtime_more: where runtime more than value. (float)
        * runtime_less: where runtime less than value. (float)
        * fail_count_more: where fail count more than value. (integer)
        * fail_count_less: where fail count less than value. (integer)
        * error_count_more: where error count more than value. (integer)
        * error_count_less: where error count less than value. (integer)
        * success_count_more: where success count more than value. (integer)
        * success_count_less: where success count less than value. (integer)
        * was_success: was success after run build, yes or no. choice from (true, false).
    """
    job = db.Job.get_by_name(job_name)

    if job:
        filters = {
            'job_id': job.id,
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

        if was_success is not None:
            filters['was_success'] = string.to_bool(was_success)

        query = db.Build.query.filter_by(**filters)

        if date_from is not None:
            date_from = string.to_datetime(date_from, no_time=True)
            query = query.filter(db.Build.date >= date_from)

        if date_to is not None:
            date_to = string.to_datetime(date_to, no_time=True, to_end_day=True)
            query = query.filter(db.Build.date <= date_to)

        if runtime_more is not None:
            query = query.filter(db.Build.runtime > string.to_float(runtime_more))
        elif runtime_less is not None:
            query = query.filter(db.Build.runtime < string.to_float(runtime_less))

        if fail_count_more is not None:
            query = query.filter(db.Build.fail_count > string.to_int(fail_count_more))
        elif fail_count_less is not None:
            query = query.filter(db.Build.fail_count < string.to_int(fail_count_less))

        if error_count_more is not None:
            query = query.filter(db.Build.error_count > string.to_int(error_count_more))
        elif error_count_less is not None:
            query = query.filter(db.Build.error_count < string.to_int(error_count_less))

        if success_count_more is not None:
            query = query.filter(db.Build.success_count > string.to_int(success_count_more))
        elif success_count_less is not None:
            query = query.filter(db.Build.success_count < string.to_int(success_count_less))

        query = paginated_query(query, flask.request)

        return make_result(
            query.all(),
            total_count=query.total_count,
            current_count=query.current_count,
            job=job,
        ), statuses.OK


@resource.route(
    '/jobs/<string:job_name>/builds/<string:build_name>/start',
    methods=['POST'],
    schema='start_build.post.json',
)
def start_build(job_name, build_name):
    """
    Start a new build.
    The mission of command is initialization a build what will glue case results.
    All statistic may be written with stop command.
    When build is created then it status is running while a build does'n stopped.

    METHOD: POST
    PATH: /api/v1/jobs/<string:job_name>/builds/<string:build_name>/start

    JSON params:

        * metadata: dictionary with contains info about your build.
            Key and value can be of string type only.
    """
    job = db.Job.get_by_name(job_name)

    if not job and flask.request.args.get(API_AUTO_CREATION_PARAM):
        job = db.Job.create(name=job_name, is_active=True)

    if job:
        json = flask.request.get_json()

        data = {
            'job_id': job.id,
            'name': build_name,
            'runtime': 0.0,
            'fail_count': 0,
            'error_count': 0,
            'tests_count': 0,
            'success_count': 0,
            'is_running': True,
            'was_success': False,

        }
        metadata = json.get('metadata')

        build = db.Build.create(**data)

        if metadata:
            build.md = metadata

        return make_result(
            build,
            job=job,
            location=api_location(
                '/jobs/{}/builds/{}',
                job_name, build_name,
                version=VERSION,
            ),
        ), statuses.CREATED


@resource.route(
    '/jobs/<string:job_name>/builds/<string:build_name>/stop',
    methods=['PUT'],
    schema='stop_build.put.json',
)
def stop_build(job_name, build_name):
    """
    Stop a build.
    The command is for creation statistic of a build what started earlier.
    A build will has status is_running=False after first call to the command with success.

    METHOD: PUT
    PATH: /api/v1/jobs/<string:job_name>/builds/<string:build_name>/stop

    JSON params:

        * runtime: time of execution (float, required)
        * was_success: was success or no (boolean, required)
        * tests_count: (integer, required)
        * success_count: (integer, required)
        * fail_count: (integer, required)
        * error_count: (integer, required)
    """
    job = db.Job.get_by_name(job_name)

    if job:
        build = db.Build.query.filter_by(
            job_id=job.id, name=build_name,
        ).first()

        if build:
            json = flask.request.get_json()

            data = {
                'is_running': False,
                'runtime': json.get('runtime'),
                'was_success': json.get('was_success'),
                'tests_count': json.get('tests_count'),
                'success_count': json.get('success_count'),
                'fail_count': json.get('fail_count'),
                'error_count': json.get('error_count'),
            }
            build.update(**data)

            return make_result(
                build,
                job=job,
                location=api_location(
                    '/jobs/{}/builds/{}',
                    job_name, build_name,
                    version=VERSION,
                ),
            ), statuses.OK


@resource.route('/jobs/<string:job_name>/builds/<string:build_name>', methods=['GET'])
def get_build_by_name(job_name, build_name):
    """
    Get only one build by name.

    METHOD: GET
    PATH: /api/v1/jobs/<string:job_name>/builds/<string:build_name>
    """
    job = db.Job.get_by_name(job_name)

    if job:
        build = db.Build.query.filter_by(
            job_id=job.id, name=build_name,
        ).first()

        if build:
            return make_result(
                build,
                job=job,
            ), statuses.OK
