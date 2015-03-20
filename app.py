# -*- coding: utf-8 -*-
#
# Author: Craig Russell <craig@craig-russell.co.uk>
# Basic Personalised Ads Beacon Endpoint


import datetime as DT
from flask import Flask, request, json, make_response, abort
from models import Customer, Visitor
from werkzeug.exceptions import HTTPException, BadRequest, InternalServerError, Conflict


app = Flask(__name__, static_folder='static', static_url_path='')
JSONP = "_ape.callback"


def make_jsonp_response(payload=dict(), status_code=200):
    """Make a jsonp response object from a payload dict"""
    payload['status_code'] = status_code
    body = "%s(%s)" % (JSONP, json.dumps(payload))
    response = make_response(body, status_code)
    response.headers['Content-Type'] = "application/javascript;charset=utf-8"
    return response


@app.route('/beacon.js')
def beacon():

    # Set our jsonp callback function first, as any exceptions may depend upon it
    global JSONP
    JSONP = request.args.get('jsonp', JSONP)

    # Get args data or defaults
    args = dict()
    args['jsonp']           = JSONP
    args['ad_prefix']       = request.args.get('ac', "ape-ad") # Ad class prefix
    args['visitor_id']      = request.args.get('cc', "")       # The APE cookie visitor_id
    args['debug']           = request.args.get('db', "")       # Debug switch
    args['page_url']        = request.args.get('dl', "")       # Page URL
    args['referrer_url']    = request.args.get('dr', "")       # Referrer URL if set
    args['page_title']      = request.args.get('dt', "")       # Page title
    args['event']           = request.args.get('ev', "")       # Event
    args['customer_id']     = request.args.get('id', "")       # The customer account ID
    args['timestamp']       = request.args.get('ld', "")       # Event timestamp
    args['language']        = request.args.get('lg', "")       # Browser language
    args['screen_colour']   = request.args.get('sc', "")       # Screen colour depth
    args['screen_height']   = request.args.get('sh', "")       # Screen height
    args['ad_unit_classes'] = request.args.get('st', "")       # The set of Ad Unit ids on this page
    args['screen_width']    = request.args.get('sw', "")       # Screen width
    args['user_agent']      = request.args.get('ua', "")       # User Agent
    args['script_version']  = request.args.get('vr', "0.0")    # Version number of this script

    # Ensure page url and customer id are provided
    if not args['page_url']:    raise BadRequest("Bad Request: Value required for page url (dl)")
    if not args['customer_id']: raise BadRequest("Bad Request: Value required for customer id (id)")

    # Extract ad unit identifiers
    ad_unit_classes = args['ad_unit_classes'].split(' ')
    ad_prefix = "%s-" % args['ad_prefix']
    args['ad_unit_ids'] = [c.lstrip(ad_prefix) for c in ad_unit_classes if c.startswith(ad_prefix)]

    # Deserialise timestamp
    args['timestamp'] = DT.datetime.fromtimestamp(int(args['timestamp']) / 1000)

    # Convert values to base data types
    args['screen_width']  = int(args['screen_width'])
    args['screen_height'] = int(args['screen_height'])
    args['screen_colour'] = int(args['screen_colour'])
    args['debug']         = (args['debug'] == "true")

    payload = dict() # The response payload

    # Respect Do Not Track
    # Formally "DNT" but Chrome sends "Dnt"
    if request.headers.get('DNT', False) or request.headers.get('Dnt', False):
        raise Conflict("Do Not Track enabled on client")
    
    # Return args in payload in debug mode
    if args['debug']:
        payload['args'] = args

    # Get customer record
    customer = Customer.get(id=args['customer_id'])
    if customer:
        
        # Ensure customer account_id is valid for this page url
        if customer.is_site_owner(url=args['page_url']):
        
            # Get/create visitor record for this customer
            visitor = customer.get_visitor(id=args['visitor_id'])
            payload['visitor_id'] = visitor.id
        
            # Update visitor data from payload args
            visitor.update_with_data(data=args)

            # Ensure we have ad classes (hence there are ads on the page)
            if args['ad_unit_ids']:

                # Get personalised ad content for this visitor for these ads
                ads = visitor.personalised_ads(ad_ids=args['ad_unit_ids'])
                
                # Format ad content for json response
                payload['ad_content'] = dict()
                for ad in ads:
                    key = "%s-%s" % (args['ad_prefix'], ad.id)
                    payload['ad_content'][key] = dict()
                    payload['ad_content'][key]['id']      = ad.id
                    payload['ad_content'][key]['styles']  = ad.styles
                    payload['ad_content'][key]['content'] = ad.content
    
    return make_jsonp_response(payload)


@app.errorhandler(HTTPException)
def handle_error(e):
    print "HTTPException: %s, %s, %s" % (e.code, e.name, e.description)
    return make_jsonp_response(dict(description=e.description, code=e.code, name=e.name), e.code)


# @app.errorhandler(Exception)
# def handle_error(e):
#     print "Exception: %s" % e
#     e = InternalServerError()
#     return make_jsonp_response(dict(description=e.description, code=e.code, name=e.name), e.code)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)