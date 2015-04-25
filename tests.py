# -*- coding: utf-8 -*-
#
# Author: Craig Russell <craig@craig-russell.co.uk>
# Unit tests

import os
import json
import unittest
from app import app as beacon

def unpack_jsonp(payload):
    """Retun object structure from JSONP payload string"""
    JSONP = '_ape.callback'
    payload = payload.lstrip(JSONP + '(').rstrip(')')
    return json.loads(payload)

class TestApp(unittest.TestCase):

    def setUp(self):
        beacon.config['TESTING'] = True
        self.beacon = beacon.test_client()

    def test_root(self):
        rv = self.beacon.get('/')
        data = unpack_jsonp(rv.data)
        self.assertEqual(rv.status_code, 200) # Response always returns with 200 in the headers
        self.assertEqual(data['status_code'], 404) # Not Found

    def test_beacon_bad_request(self):
        # Request without required params
        rv = self.beacon.get('/beacon.js')
        data = unpack_jsonp(rv.data)
        self.assertEqual(rv.mimetype, "application/javascript")
        self.assertEqual(rv.status_code, 200) # Response always returns with 200 in the headers
        self.assertEqual(data['status_code'], 400) # Bad Request

        # Request with Page URL
        rv = self.beacon.get('/beacon.js?dl=http%3A//example.com')
        data = unpack_jsonp(rv.data)
        self.assertEqual(rv.mimetype, "application/javascript")
        self.assertEqual(rv.status_code, 200) # Response always returns with 200 in the headers
        self.assertEqual(data['status_code'], 400) # Bad Request

        # Request with Customer ID
        rv = self.beacon.get('/beacon.js?id=123456')
        data = unpack_jsonp(rv.data)
        self.assertEqual(rv.mimetype, "application/javascript")
        self.assertEqual(rv.status_code, 200) # Response always returns with 200 in the headers
        self.assertEqual(data['status_code'], 400) # Bad Request


if __name__ == "__main__":
    unittest.main()