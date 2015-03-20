# -*- coding: utf-8 -*-
#
# Author: Craig Russell <craig@craig-russell.co.uk>
# Models for use in APE
#
# Customer
# Visitor
# Advert

import time
import uuid
from types import *


class PersonalisedAd(object):

    def __init__(self, id, content, styles):
        """Construct an advert with personalised content and styles"""
        self.id      = id
        self.content = content
        self.styles  = styles


class Visitor(object):

    def __init__(self, customer, id=None):
        """Construct a Visitor object, for a customer, with an optional or random id"""
        self.id       = id if id else uuid.uuid4()
        self.customer = customer
        self.data_id  = "%s-%s" % (self.customer.id, self.id)

    def update_with_data(self, data):
        """Update this Visitor record with the payload data"""
        # TODO save data in NoSQL db using self.data_id
        return self

    def data(self):
        """Return full data for this visitor in basic data types"""
        # TODO Load data from DB
        return dict()

    def segments(self):
        """Return a list of segments assigned to this visitor"""
        # TODO Load data from DB
        return list()

    def personalised_ads(self, ad_ids=[]):
        """Return all ads with personalised content for this visitor. Optionally filter by ad_ids."""
        # TODO Load data from DB
        return [
            PersonalisedAd(id  ='W3P0xOxK3rLV',
                content='<strong>Ad Number One</strong><br><a href="#">Buy Things!</a>',
                styles ='.ape-ad-W3P0xOxK3rLV {color: red;}'),
            PersonalisedAd(id  ='A9GDeXaib6kZ',
                content='<strong>Ad Number Two</strong><br><a href="#">Buy Things!</a>',
                styles ='.ape-ad-A9GDeXaib6kZ {color: green;}'),
            PersonalisedAd(id  ='oXjwYAV0bd9T',
                content='<strong>Ad Number Three</strong><br><a href="#">Buy Things!</a>',
                styles ='.ape-ad-oXjwYAV0bd9T {color: blue;}'),
            PersonalisedAd(id  ='nNQQOYbFBbPI',
                content='<strong>Ad Number Four</strong><br><a href="#">Buy Things!</a>',
                styles ='.ape-ad-nNQQOYbFBbPI {color: purple;}'),
        ]


class Customer(object):

    def __init__(self, id):
        """Construct a Customer object with id"""
        self.id = id

    def is_site_owner(self, url):
        """Test if this customer is owner over this site"""
        return True

    def get_visitor(self, id=None):
        """Return Visitor object with id belonging to this customer"""
        return Visitor(self, id)

    @classmethod
    def get(cls, id):
        """Return Customer object with id"""
        return Customer(id)


if __name__ == "__main__":

    ## RUN UNIT TESTS ##
    import unittest


    class AdvertModel(unittest.TestCase):

        def test_constructor(self):
            a = Advert(id='demo-id', content='Demo Content')
            self.assertEqual(a.id,      "demo-id")
            self.assertEqual(a.content, "Demo Content")
            

    class VisitorModel(unittest.TestCase):

        def setUp(self):
            self.customer = Customer(id="demo-id")

        def test_constructor(self):
            v = Visitor(self.customer, 'demo-id')
            self.assertEqual(v.id, "demo-id")

            v = Visitor(self.customer)
            self.assertEqual(v.id, "visitor-123") # Generated

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

        def test_personalised_ads(self):
            v = Visitor(self.customer, 'demo-id')
            self.assertIsInstance(v.personalised_ads(), list)


    class CustomerModel(unittest.TestCase):

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

            v = c.get_visitor()
            self.assertIs(v.customer, c)
            self.assertEqual(v.id, "visitor-123") # generated

        def test_is_site_owner(self):
            c = Customer(id='demo-id')
            self.assertTrue(c.is_site_owner("http://example.com/path"))


    unittest.main(verbosity=2)