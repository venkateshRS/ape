# -*- coding: utf-8 -*-
#
# Author: Craig Russell <craig@craig-russell.co.uk>
# Models for use in APE
#
# Component : A personalised section of page content
# Visitor : A visitor to a site
# Customer : A site owner

import time
import uuid


class Component(object):

    def __init__(self, id, content, styles=""):
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

    def components(self, ad_ids=[]):
        """Return all ads with personalised content for this visitor. Optionally filter by ad_ids."""
        # TODO Load data from DB
        return [
            Component(id  ='W3P0xOxK3rLV',
                content='<strong>Ad Number One</strong><br><a href="#">Buy Things!</a>',
                styles ='.ape-W3P0xOxK3rLV {color: red;}'),
            Component(id  ='A9GDeXaib6kZ',
                content='<strong>Ad Number Two</strong><br><a href="#">Buy Things!</a>',
                styles ='.ape-A9GDeXaib6kZ {color: green;}'),
            Component(id  ='oXjwYAV0bd9T',
                content='<strong>Ad Number Three</strong><br><a href="#">Buy Things!</a>',
                styles ='.ape-oXjwYAV0bd9T {color: blue;}'),
            Component(id  ='nNQQOYbFBbPI',
                content='<strong>Ad Number Four</strong><br><a href="#">Buy Things!</a>',
                styles ='.ape-nNQQOYbFBbPI {color: purple;}'),
        ]
       
    @classmethod
    def get(cls, customer, id):
      """Return visitor object with id, for customer"""
      # TODO Find visitor
      return Visitor(customer, id)
      


class Customer(object):

    def __init__(self, id):
        """Construct a Customer object with id"""
        self.id = id

    def is_site_owner(self, url):
        """Test if this customer is owner over this site"""
        # TODO Test site ownership
        return True

    def get_visitor(self, id=None):
        """Return Visitor object with id, belonging to this customer"""
        return Visitor.get(self, id)

    @classmethod
    def get(cls, id):
        """Return Customer object with id"""
        # TODO Find customer
        return Customer(id)