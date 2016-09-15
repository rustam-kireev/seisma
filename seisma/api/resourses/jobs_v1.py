# -*- coding: utf-8 -*-

from http import HTTPStatus as statuses

import flask

from ..result import make_result
from ..utils import api_location
from ..resource import ApiResource
from ..utils import paginated_query
from ...database import schema as db


VERSION = 1


resource = ApiResource(__name__, version=VERSION)


@resource.route('/jobs', methods=['GET'])
def get_jobs():
    """
    Get list of jobs.

    METHOD: GET
    PATH: /api/v1/jobs

    GET params

        * from: for pagination. (integer)
        * to: for pagination. (integer)
    """
    query = db.Job.query.filter_by(is_active=True)
    query = paginated_query(query, flask.request)

    return make_result(
        query.all(),
        total_count=query.total_count,
        current_count=query.current_count,
    ), statuses.OK


@resource.route('/jobs/<string:job_name>', methods=['POST'], schema='job.post.json')
def create_job(job_name):
    """
    Create job.

    METHOD: POST
    PATH: /api/v1/jobs

    JSON params

        * description: description of job (string)
    """
    json = flask.request.get_json()

    data = {
        'is_active': True,
        'name': job_name,
        'description': json.get('description', ''),
    }
    job = db.Job.create(**data)

    return make_result(
        job,
        location=api_location(
            '/jobs/{}', job_name, version=VERSION,
        ),
    ), statuses.CREATED


@resource.route('/jobs/<string:job_name>', methods=['GET'])
def get_job_by_name(job_name):
    """
    Get only one job by name.

    METHOD: GET
    PATH: /api/v1/jobs/<string:job_name>
    """
    job = db.Job.get_by_name(job_name)

    if job:
        return make_result(job), statuses.OK


@resource.route('/jobs/<string:job_name>', methods=['DELETE'])
def delete_job_by_name(job_name):
    """
    Delete job by name.

    METHOD: DELETE
    PATH: /api/v1/jobs/<string:job_name>
    """
    job = db.Job.get_by_name(job_name)

    if job:
        job.update(is_active=False)
        return make_result(job), statuses.OK
