# -*- coding: utf-8 -*-
#
# Author: Craig Russell <craig@craig-russell.co.uk>
# Unit tests

import os
import unittest
from app import app as beacon

class TestApp(unittest.TestCase):

    def setUp(self):
        beacon.config['TESTING'] = True
        self.beacon = beacon.test_client()

    def test_root(self):
        rv = self.beacon.get('/')
        self.assertEqual(rv.status_code, 404) # Not Found

    def test_beacon_bad_request(self):
        # Request without required params
        rv = self.beacon.get('/beacon.js')
        self.assertEqual(rv.mimetype, "application/javascript")
        self.assertEqual(rv.status_code, 400) # Bad Request

        # Request with Page URL
        rv = self.beacon.get('/beacon.js?dl=http%3A//example.com')
        self.assertEqual(rv.mimetype, "application/javascript")
        self.assertEqual(rv.status_code, 400) # Bad Request

        # Request with Customer ID
        rv = self.beacon.get('/beacon.js?id=123456')
        self.assertEqual(rv.mimetype, "application/javascript")
        self.assertEqual(rv.status_code, 400) # Bad Request


if __name__ == "__main__":
    unittest.main()