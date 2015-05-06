# -*- coding: utf-8 -*-
#
# Author: Craig Russell <craig@craig-russell.co.uk>
# Unit tests

import os
import json
import logging
import unittest
import datetime as DT
from app import app as beacon
from models import Customer, Visitor, Component

def unpack_jsonp(payload, callback="_ape.callback"):
    """Retun object structure from JSONP payload string"""
    payload = payload.lstrip(callback + '(').rstrip(')')
    return json.loads(payload)

class TestApp(unittest.TestCase):

    def setUp(self):
        beacon.config['TESTING'] = True
        logging.disable(logging.CRITICAL)
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

        # Request with Page URL (dl)
        rv = self.beacon.get('/beacon.js?dl=http%3A//example.com')
        data = unpack_jsonp(rv.data)
        self.assertEqual(rv.mimetype, "application/javascript")
        self.assertEqual(rv.status_code, 200) # Response always returns with 200 in the headers
        self.assertEqual(data['status_code'], 400) # Bad Request

        # Request with Customer ID (id)
        rv = self.beacon.get('/beacon.js?id=123456')
        data = unpack_jsonp(rv.data)
        self.assertEqual(rv.mimetype, "application/javascript")
        self.assertEqual(rv.status_code, 200) # Response always returns with 200 in the headers
        self.assertEqual(data['status_code'], 400) # Bad Request

    def test_beacon_debug(self):
        # debug not provided
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com')
        data = unpack_jsonp(rv.data)
        self.assertNotIn('args', data) # args not returned
        
        # debug provided (db)
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true')
        data = unpack_jsonp(rv.data)
        self.assertIn('args', data) # args returned
        self.assertIn('debug', data['args'])
        self.assertTrue(data['args']['debug'])

    def test_beacon_jsonp(self):
        # jsonp not provided
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true')
        data = unpack_jsonp(rv.data)
        self.assertTrue(rv.data.startswith('_ape.callback'))
        self.assertIsInstance(data, dict)
        
        # jsonp provided (jsonp)
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true&jsonp=foobar')
        self.assertTrue(rv.data.startswith('foobar'))
        data = unpack_jsonp(payload=rv.data, callback='foobar')
        self.assertIsInstance(data, dict)

        # configurable callback in error response
        rv = self.beacon.get('/beacon.js?jsonp=foobar')
        self.assertTrue(rv.data.startswith('foobar'))
        data = unpack_jsonp(payload=rv.data, callback='foobar')
        self.assertIsInstance(data, dict)


    def test_beacon_visitor_id(self):
        # visitor_id not provided
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true')
        data = unpack_jsonp(rv.data)
        self.assertIn('visitor_id', data.keys()) # new visitor id returned
        
        # visitor_id provided (cc)
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true&cc=foobar')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['visitor_id'], 'foobar')

    def test_beacon_referrer_url(self):
        # referrer_url not provided
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['referrer_url'], "")
        
        # referrer_url provided (dr)
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true&dr=foobar')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['referrer_url'], "foobar")

    def test_beacon_page_title(self):
        # page_title not provided
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['page_title'], "")
        
        # page_title provided (dt)
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true&dt=foobar')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['page_title'], "foobar")

    def test_beacon_event(self):
        # event not provided
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['event'], "")
        
        # event provided (ev)
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true&ev=foobar')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['event'], "foobar")

    def test_beacon_timestamp(self):
        # timestamp not provided
        format = "%a, %d %b %Y %H:%M:%S %Z"

        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true')
        data = unpack_jsonp(rv.data)
        timestamp = data['args']['timestamp']
        self.assertIsInstance(DT.datetime.strptime(timestamp, format), DT.datetime)
        
        # timestamp provided (ld)
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true&ld=1490916389')
        data = unpack_jsonp(rv.data)
        timestamp = data['args']['timestamp']
        self.assertIsInstance(DT.datetime.strptime(timestamp, format), DT.datetime)
        self.assertEqual(DT.datetime.strptime(timestamp, format), DT.datetime.utcfromtimestamp(1490916389/1000))

    def test_beacon_language(self):
        # language not provided
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['language'], "")
        
        # language provided (lg)
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true&lg=foobar')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['language'], "foobar")

    def test_beacon_placeholders(self):
        # placeholders not provided
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['placeholders'], "")
        
        # placeholders provided (pc)
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true&pc=ape-foo%20ape-bar%20foo-bar')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['placeholders'], "ape-foo ape-bar foo-bar")

    def test_beacon_prefix(self):
        # prefix not provided
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true&pc=ape-foo%20ape-bar%20foo-baz')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['prefix'], "ape")
        self.assertEqual(data['args']['placeholder_ids'], ["foo", "bar"])
        
        # prefix provided (px)
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true&pc=ape-foo%20ape-bar%20foo-baz&px=foo')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['prefix'], "foo")
        self.assertEqual(data['args']['placeholder_ids'], ["baz"])

    def test_beacon_screen_colour(self):
        # screen_colour not provided
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['screen_colour'], 0)
        
        # screen_colour provided (sc)
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true&sc=64')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['screen_colour'], 64)

    def test_beacon_screen_height(self):
        # screen_height not provided
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['screen_height'], 0)
        
        # screen_height provided (sh)
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true&sh=1000')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['screen_height'], 1000)

    def test_beacon_screen_width(self):
        # screen_width not provided
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['screen_width'], 0)
        
        # screen_width provided (sw)
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true&sw=1000')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['screen_width'], 1000)

    def test_beacon_user_agent(self):
        # user_agent not provided
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['user_agent'], "")
        
        # user_agent provided (ua)
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true&ua=foobar')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['user_agent'], "foobar")

    def test_beacon_script_version(self):
        # script_version not provided
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['script_version'], "0.0")
        
        # script_version provided (vr)
        rv = self.beacon.get('/beacon.js?id=foo&dl=http%3A//bar.com&db=true&vr=1.0')
        data = unpack_jsonp(rv.data)
        self.assertEqual(data['args']['script_version'], "1.0")


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