# -*- coding: utf-8 -*-

import unittest

from ... import json
from ... import wsgi


class BaseApiTestCse(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.app = wsgi.app.test_client()

    def tearDown(self):
        self.app = None

    def post(self, path, data, *args, **kwargs):
        return self.app.post(
            path, data=json.dumps(data),
            content_type='application/json',
            *args, **kwargs
        )

    def get(self, *args, **kwargs):
        return self.app.get(*args, **kwargs)

    def put(self, path, data, *args, **kwargs):
        return self.app.put(
            path, data=json.dumps(data),
            content_type='application/json',
            *args, **kwargs
        )

    def delete(self, *args, **kwargs):
        return self.app.put(*args, **kwargs)

    @staticmethod
    def get_json(resp):
        return json.loads(resp.data.decode('utf-8'))
