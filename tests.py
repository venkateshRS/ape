# -*- coding: utf-8 -*-
#
# Author: Craig Russell <craig@craig-russell.co.uk>
# Unit tests

import os
import json
import unittest
from app import app as beacon
from models import Customer, Visitor, Component

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


class TestComponentModel(unittest.TestCase):

    def test_constructor(self):
        a = Component(id='demo-id', content='Demo Content', styles="xxx")
        self.assertEqual(a.id,      "demo-id")
        self.assertEqual(a.content, "Demo Content")
        self.assertEqual(a.styles,  "xxx")
        

class TestVisitorModel(unittest.TestCase):

    def setUp(self):
        self.customer = Customer(id="demo-id")

    def test_constructor(self):
        v = Visitor(self.customer, 'demo-id')
        self.assertEqual(v.id, "demo-id")
        
    def test_get(self):
        v = Visitor.get(self.customer, "demo-id")
        self.assertEqual(v.id, "demo-id")
        self.assertEqual(v.customer, self.customer)

    def test_update_with_data(self):
        v1 = Visitor(self.customer, 'demo-id')
        v2 = v1.update_with_data(dict())
        self.assertIsInstance(v2, Visitor)
        self.assertEqual(v1.id, v2.id)

    def test_data(self):
        v = Visitor(self.customer, 'demo-id')
        self.assertIsInstance(v.data(), dict)

    def test_segments(self):
        v = Visitor(self.customer, 'demo-id')
        self.assertIsInstance(v.segments(), list)

    def test_components(self):
        v = Visitor(self.customer, 'demo-id')
        self.assertIsInstance(v.components(), list)


class TestCustomerModel(unittest.TestCase):

    def test_constructor(self):
        c = Customer('demo-id')
        self.assertEqual(c.id, "demo-id")

    def test_get(self):
        c = Customer.get(id="demo-id")
        self.assertEqual(c.id, "demo-id")

    def test_get_visitor(self):
        c = Customer(id='demo-id')
        v = c.get_visitor(id='demo-id')
        self.assertIs(v.customer, c)
        self.assertEqual(v.id, "demo-id")

    def test_is_site_owner(self):
        c = Customer(id='demo-id')
        self.assertTrue(c.is_site_owner("http://example.com/path"))


if __name__ == "__main__":
    unittest.main()