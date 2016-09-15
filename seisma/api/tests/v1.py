# -*- coding: utf-8 -*-

from .tools import random_name
from .base import BaseApiTestCse


job = None
build = None

case = None
case_result = None


class TestFullCycle(BaseApiTestCse):

    def test_01_job_does_not_exist(self):
        resp = self.get('/api/v1/jobs/qweasdzxc')
        self.assertEqual(resp.status_code, 404)

    def test_02_create_job(self):
        global job

        name = random_name()
        data = {
            'description': 'It is a build from test',
        }
        resp = self.post('/api/v1/jobs/{}'.format(name), data)
        self.assertEqual(resp.status_code, 201)

        job = self.get_json(resp)
        self.assertEqual(job['result']['name'], name)
        self.assertEqual(job['result']['description'], data['description'])

    def test_03_case_does_not_exist(self):
        resp = self.get('/api/v1/jobs/{}/cases/asdzxsdfgcscd'.format(job['result']['name']))
        self.assertEqual(resp.status_code, 404)

    def test_04_create_case(self):
        global case

        name = random_name()
        data = {
            'description': 'It is a case from test',
        }
        resp = self.post(
            '/api/v1/jobs/{}/cases/{}'.format(
                job['result']['name'],
                name,
            ),
            data,
        )
        self.assertEqual(resp.status_code, 201)

        case = self.get_json(resp)
        self.assertEqual(case['result']['name'], name)
        self.assertEqual(case['result']['description'], data['description'])

    def test_05_build_does_not_exist(self):
        resp = self.get('/api/v1/jobs/{}/builds/asdvslfjsdjf'.format(job['result']['name']))
        self.assertEqual(resp.status_code, 404)

    def test_06_start_build(self):
        global build

        name = random_name()
        data = {
            'metadata': {
                'issue': 'http://localhost/TRG-13432',
            },
        }
        resp = self.post('/api/v1/jobs/{}/builds/{}/start'.format(job['result']['name'], name), data)
        self.assertEqual(resp.status_code, 201)

        build = self.get_json(resp)

        self.assertEqual(build['result']['name'], name)
        self.assertEqual(build['result']['is_running'], True)
        self.assertEqual(build['result']['was_success'], False)
        self.assertDictEqual(build['result']['metadata'], data['metadata'])

    def test_07_stop_build(self):
        global build

        data = {
            'was_success': True,
            'success_count': 100,
            'tests_count': 110,
            'error_count': 3,
            'fail_count': 7,
            'runtime': 148.46,
        }
        resp = self.put(
            '/api/v1/jobs/{}/builds/{}/stop'.format(
                job['result']['name'],
                build['result']['name'],
            ),
            data,
        )

        build = self.get_json(resp)

        for k in data:
            self.assertEqual(data[k], build['result'][k], '{}'.format(k))
        self.assertEqual(build['result']['is_running'], False)

    def test_08_case_result_does_not_exist(self):
        resp = self.get(
            '/api/v1/jobs/{}/builds/{}/cases/sdkjjksdjkncd'.format(
                job['result']['name'],
                build['result']['name'],
            ),
        )
        self.assertEqual(resp.status_code, 404)

    def test_09_create_case_result(self):
        global case_result

        data = {
            'reason': 'some reason',
            'runtime': 30.23,
            'status': 'passed',
            'metadata': {
                'issue': 'http://localhost/TRG-13432',
            },
        }
        resp = self.post(
            '/api/v1/jobs/{}/builds/{}/cases/{}'.format(
                job['result']['name'],
                build['result']['name'],
                case['result']['name'],
            ),
            data,
        )
        self.assertEqual(resp.status_code, 201)

        case_result = self.get_json(resp)

        for k in data:
            self.assertEqual(data[k], case_result['result'][k], '{}'.format(k))

        self.assertDictEqual(case_result['result']['metadata'], data['metadata'])

    def test_10_get_job(self):
        resp = self.get(job['extra'].pop('location'))
        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(job, self.get_json(resp))

    def test_11_get_case(self):
        resp = self.get(case['extra'].pop('location'))
        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(case, self.get_json(resp))

    def test_12_get_build(self):
        resp = self.get(build['extra'].pop('location'))
        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(build, self.get_json(resp))

    def test_13_get_case_result(self):
        resp = self.get(case_result['extra'].pop('location'))
        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(case_result, self.get_json(resp))

    def test_14_get_job_list(self):
        resp = self.get('/api/v1/jobs')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(job['result'], self.get_json(resp)['result'])

    def test_15_get_case_list_from_job(self):
        resp = self.get('/api/v1/jobs/{}/cases'.format(job['result']['name']))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(case['result'], self.get_json(resp)['result'])

    def test_16_get_build_list_from_job(self):
        resp = self.get('/api/v1/jobs/{}/builds'.format(job['result']['name']))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(build['result'], self.get_json(resp)['result'])

    def test_17_get_case_stats(self):
        resp = self.get(
            '/api/v1/jobs/{}/cases/{}/stat'.format(
                job['result']['name'],
                case['result']['name'],
            ),
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(case_result['result'], self.get_json(resp)['result'])

    def test_18_get_builds_by_dates(self):
        resp = self.get(
            '/api/v1/jobs/{}/builds?data_from=2015-03-23&date_to=2015-04-20'.format(
                job['result']['name'],
            ),
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(self.get_json(resp)['result'])

        resp = self.get(
            '/api/v1/jobs/{}/builds'.format(
                job['result']['name'],
            ),
        )
        self.assertEqual(resp.status_code, 200)
        data = self.get_json(resp)
        self.assertTrue(data['result'])
        self.assertEqual(data['extra']['total_count'], 1)
        self.assertEqual(data['extra']['current_count'], 1)

    def test_19_get_stat_of_cases_from_job(self):
        resp = self.get('/api/v1/jobs/{}/cases/stat'.format(job['result']['name']))
        data = self.get_json(resp)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(data['result']), 1)
        self.assertIn(case_result['result'], data['result'])
