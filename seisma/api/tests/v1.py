# -*- coding: utf-8 -*-

from .tools import random_name
from .base import BaseApiTestCse


build = None
build_result = None

case = None
case_result = None


class TestFullCycle(BaseApiTestCse):

    def test_01_build_does_not_exist(self):
        resp = self.get('/api/v1/builds/qweasdzxc')
        self.assertEqual(resp.status_code, 404)

    def test_02_create_build(self):
        global build

        data = {
            'name': random_name(),
            'description': 'It is a build from test',
        }
        resp = self.post('/api/v1/builds', data)
        self.assertEqual(resp.status_code, 201)

        build = self.get_json(resp)
        self.assertEqual(build['result']['name'], data['name'])
        self.assertEqual(build['result']['description'], data['description'])

    def test_03_case_does_not_exist(self):
        resp = self.get('/api/v1/builds/{}/cases/asdzxsdfgcscd'.format(build['result']['name']))
        self.assertEqual(resp.status_code, 404)

    def test_04_create_case(self):
        global case

        data = {
            'name': random_name(),
            'description': 'It is a case from test',
        }
        resp = self.post('/api/v1/builds/{}/cases'.format(build['result']['name']), data)
        self.assertEqual(resp.status_code, 201)

        case = self.get_json(resp)
        self.assertEqual(case['result']['name'], data['name'])
        self.assertEqual(case['result']['description'], data['description'])

    def test_05_build_result_does_not_exist(self):
        resp = self.get('/api/v1/builds/{}/results/asdvslfjsdjf'.format(build['result']['name']))
        self.assertEqual(resp.status_code, 404)

    def test_06_create_build_result(self):
        global build_result

        data = {
            'name': random_name(),
            'metadata': {
                'issue': 'http://localhost/TRG-13432',
            },
        }
        resp = self.post('/api/v1/builds/{}/results'.format(build['result']['name']), data)
        self.assertEqual(resp.status_code, 201)

        build_result = self.get_json(resp)

        for k in data:
            self.assertEqual(data[k], build_result['result'][k], '{}'.format(k))

        self.assertDictEqual(build_result['result']['metadata'], data['metadata'])

    def test_07_update_build_result(self):
        global build_result

        data = {
            'was_success': True,
            'success_count': 100,
            'tests_count': 110,
            'error_count': 3,
            'fail_count': 7,
            'runtime': 148.46,
        }
        resp = self.put(
            '/api/v1/builds/{}/results/{}'.format(
                build['result']['name'],
                build_result['result']['name'],
            ),
            data,
        )

        build_result = self.get_json(resp)

        for k in data:
            self.assertEqual(data[k], build_result['result'][k], '{}'.format(k))

    def test_08_case_result_does_not_exist(self):
        resp = self.get(
            '/api/v1/builds/{}/results/{}/cases/sdkjjksdjkncd'.format(
                build['result']['name'],
                build_result['result']['name'],
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
            '/api/v1/builds/{}/results/{}/cases/{}'.format(
                build['result']['name'],
                build_result['result']['name'],
                case['result']['name'],
            ),
            data,
        )
        self.assertEqual(resp.status_code, 201)

        case_result = self.get_json(resp)

        for k in data:
            self.assertEqual(data[k], case_result['result'][k], '{}'.format(k))

        self.assertDictEqual(case_result['result']['metadata'], data['metadata'])

    def test_10_get_build(self):
        resp = self.get('/api/v1/builds/{}'.format(build['result']['name']))
        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(build, self.get_json(resp))

    def test_11_get_case(self):
        resp = self.get(
            '/api/v1/builds/{}/cases/{}'.format(
                build['result']['name'],
                case['result']['name'],
            ),
        )
        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(case, self.get_json(resp))

    def test_12_get_build_result(self):
        resp = self.get(
            '/api/v1/builds/{}/results/{}'.format(
                build['result']['name'],
                build_result['result']['name'],
            ),
        )
        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(build_result, self.get_json(resp))

    def test_13_get_case_result(self):
        resp = self.get(
            '/api/v1/builds/{}/results/{}/cases/{}'.format(
                build['result']['name'],
                build_result['result']['name'],
                case['result']['name'],
            ),
        )
        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(case_result, self.get_json(resp))

    def test_14_get_build_list(self):
        resp = self.get('/api/v1/builds')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(build['result'], self.get_json(resp)['result'])

    def test_15_get_case_list(self):
        resp = self.get('/api/v1/builds/{}/cases'.format(build['result']['name']))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(case['result'], self.get_json(resp)['result'])

    def test_16_get_build_result_list(self):
        resp = self.get('/api/v1/builds/{}/results'.format(build['result']['name']))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(build_result['result'], self.get_json(resp)['result'])

    def test_17_get_case_result_list(self):
        resp = self.get(
            '/api/v1/builds/{}/cases/{}/results'.format(
                build['result']['name'],
                case['result']['name'],
            ),
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(case_result['result'], self.get_json(resp)['result'])

    def test_18_get_build_results_by_dates(self):
        resp = self.get(
            '/api/v1/builds/{}/results?data_from=2015-03-23&date_to=2015-04-20'.format(
                build['result']['name'],
            ),
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(self.get_json(resp)['result'])

        resp = self.get(
            '/api/v1/builds/{}/results'.format(
                build['result']['name'],
            ),
        )
        self.assertEqual(resp.status_code, 200)
        data = self.get_json(resp)
        self.assertTrue(data['result'])
        self.assertEqual(data['extra']['total_count'], 1)
        self.assertEqual(data['extra']['current_count'], 1)

    def test_19_get_all_case_results_from_build(self):
        resp = self.get('/api/v1/builds/{}/cases/results'.format(build['result']['name']))
        data = self.get_json(resp)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(data['result']), 1)
        self.assertIn(case_result['result'], data['result'])
