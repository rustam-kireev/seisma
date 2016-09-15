# -*- coding: utf-8 -*-

from http import HTTPStatus as statuses

import flask

from .. import string
from ..result import make_result
from ..resource import ApiResource
from ..utils import paginated_query
from ...database import schema as db
from ...constants import API_AUTO_CREATION_PARAM


resource = ApiResource(__name__, version=1)


@resource.route('/jobs/<string:job_name>/cases/<string:case_name>', methods=['GET'])
def get_case_from_job(job_name, case_name):
    """
    Get only ony case from job by name.

    METHOD: GET
    PATH: /api/v1/jobs/<string:job_name>/cases/<string:case_name>
    """
    job = db.Job.get_by_name(job_name)

    if job:
        case = db.Case.query.filter_by(job_id=job.id, name=case_name).first()

        if case:
            return make_result(
                case,
                job=job,
            ), statuses.OK


@resource.route('/jobs/<string:job_name>/cases/<string:case_name>', methods=['POST'], schema='case.post.json')
def add_case_to_job(job_name, case_name):
    """
    Add case to job, statistic about case stored separated of case data.

    METHOD: POST
    PATH: /api/v1/jobs/<string:job_name>/cases/<string:case_name>

    JSON params

        * description: about case. it's can be docstring for example (string)
    """
    job = db.Job.get_by_name(job_name)

    if job:
        json = flask.request.get_json()

        data = {
            'job_id': job.id,
            'name': case_name,
            'description': json.get('description', ''),
        }
        case = db.Case.create(**data)

        return make_result(
            case,
            job=job,
        ), statuses.CREATED


@resource.route('/jobs/<string:job_name>/cases', methods=['GET'])
def get_cases_from_job(job_name):
    """
    Get list of cases from job.

    METHOD: GET
    PATH: /api/v1/jobs/<string:job_name>/cases

    GET params

        * from: for pagination. (integer)
        * to: for pagination. (integer)
    """
    job = db.Job.get_by_name(job_name)

    if job:
        query = db.Case.query.filter_by(job_id=job.id)
        query = paginated_query(query, flask.request)

        return make_result(
            query.all(),
            total_count=query.total_count,
            current_count=query.current_count,
            job=job,
        ), statuses.OK


@resource.route('/jobs/<string:job_name>/cases/<string:case_name>/stat', methods=['GET'])
def get_stats_of_case_from_job(job_name, case_name):
    """
    Get statistic of case from job.

    METHOD: GET
    PATH: /api/v1/jobs/<string:job_name>/cases/<string:case_name>/stat

    GET params

        * from: for pagination. (integer)
        * to: for pagination. (integer)
        * status: can be in (passed, skipped, failed, error)
        * date_from: range from date (use with date_to only)
        * date to: range to date (use with date_from only)
        * runtime_more: where runtime more than value. (float)
        * runtime_less: where runtime less than value. (float)
    """
    job = db.Job.get_by_name(job_name)

    if job:
        case = db.Case.query.filter_by(job_id=job.id, name=case_name).first()

        if case:
            status = flask.request.args.get('status', None)
            date_to = flask.request.args.get('date_to', None)
            date_from = flask.request.args.get('date_from', None)
            runtime_more = flask.request.args.get('runtime_more', None)
            runtime_less = flask.request.args.get('runtime_less', None)

            query = db.CaseResult.query.filter_by(case_id=case.id)

            if status in db.CASE_STATUSES_CHOICE:
                query = query.filter(db.CaseResult.status == status)

            if date_from is not None:
                date_from = string.to_datetime(date_from, no_time=True)
                query = query.filter(db.CaseResult.date >= date_from)

            if date_to is not None:
                date_to = string.to_datetime(date_to, no_time=True, to_end_day=True)
                query = query.filter(db.CaseResult.date <= date_to)

            if runtime_more is not None:
                query = query.filter(db.CaseResult.runtime > string.to_float(runtime_more))
            elif runtime_less is not None:
                query = query.filter(db.CaseResult.runtime < string.to_float(runtime_less))

            query = paginated_query(query, flask.request)

            return make_result(
                query.all(),
                total_count=query.total_count,
                current_count=query.current_count,
                job=job,
                case=case,
            ), statuses.OK


@resource.route(
    '/jobs/<string:job_name>/builds/<string:build_name>/cases/<string:case_name>',
    methods=['POST'],
    schema='case_result.post.json',
)
def add_case_to_build(job_name, build_name, case_name):
    """
    Add case to a build.

    METHOD: POST
    PATH: /api/v1/jobs/<string:job_name>/builds/<string:build_name>/cases/<string:case_name>

    JSON params

        * status: choice from (passed, skipped, failed, error) (required)
        * runtime: time of execution (float, required)
        * reason: crush's reason (string)
        * metadata: dictionary with contains info about case result.
            Key and value can be of string type only.
    """
    job = db.Job.get_by_name(job_name)

    if job:
        build = db.Build.query.filter_by(job_id=job.id, name=build_name).first()

        if build:
            case = db.Case.query.filter_by(job_id=job.id, name=case_name).first()

            if not case and flask.request.args.get(API_AUTO_CREATION_PARAM):
                case = db.Case.create(name=case_name, job_id=job.id)

            if case:
                json = flask.request.get_json()

                data = {
                    'case_id': case.id,
                    'build_id': build.id,
                    'status': json.get('status'),
                    'runtime': json.get('runtime'),
                    'reason': json.get('reason', ''),
                }
                metadata = json.get('metadata')

                case_result = db.CaseResult.create(**data)

                if metadata:
                    case_result.md = metadata

                return make_result(
                    case_result,
                    job=job,
                    case=case,
                    build=build,
                ), statuses.CREATED


@resource.route(
    '/jobs/<string:job_name>/builds/<string:build_name>/cases/<string:case_name>',
    methods=['GET'],
)
def get_case_from_build(job_name, build_name, case_name):
    """
    Get only one case result from a build by case name.

    METHOD: GET
    PATH: /api/v1/jobs/<string:job_name>/builds/<string:build_name>/cases/<string:case_name>
    """
    job = db.Job.get_by_name(job_name)

    if job:
        build = db.Build.query.filter_by(job_id=job.id, name=build_name).first()

        if build:
            case = db.Case.query.filter_by(job_id=job.id, name=case_name).first()

            if case:
                case_result = db.CaseResult.query.filter_by(
                    build_id=build.id, case_id=case.id,
                ).first()

                if case_result:
                    return make_result(
                        case_result,
                        job=job,
                        case=case,
                        build=build,
                    ), statuses.OK


@resource.route('/jobs/<string:job_name>/cases/stat')
def get_cases_stats_from_job(job_name):
    """
    Get statistic of cases from job.

    METHOD: GET
    PATH: /api/v1/jobs/<string:job_name>/cases/stat

    GET params

        * status: can be in (passed, skipped, failed, error)
        * date_from: range from date
        * date to: range to date
        * runtime_more: where runtime more than value. (float)
        * runtime_less: where runtime less than value. (float)
    """
    job = db.Job.get_by_name(job_name)

    if job:
        status = flask.request.args.get('status', None)
        date_to = flask.request.args.get('date_to', None)
        date_from = flask.request.args.get('date_from', None)
        runtime_more = flask.request.args.get('runtime_more', None)
        runtime_less = flask.request.args.get('runtime_less', None)

        query = db.CaseResult.query.join(
            db.Build,
        ).filter(db.Build.job_id == job.id)

        if date_from is not None:
            date_from = string.to_datetime(date_from, no_time=True)
            query = query.filter(db.CaseResult.date >= date_from)

        if date_to is not None:
            date_to = string.to_datetime(date_to, no_time=True, to_end_day=True)
            query = query.filter(db.CaseResult.date <= date_to)

        if status in db.CASE_STATUSES_CHOICE:
            query = query.filter(db.CaseResult.status == status)

        if runtime_more is not None:
            query = query.filter(db.CaseResult.runtime > string.to_float(runtime_more))
        elif runtime_less is not None:
            query = query.filter(db.CaseResult.runtime < string.to_float(runtime_less))

        query = paginated_query(query, flask.request)

        return make_result(
            query.all(),
            total_count=query.total_count,
            current_count=query.current_count,
            job=job,
        ), statuses.OK
