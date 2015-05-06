# -*- coding: utf-8 -*-
#
# Author: Craig Russell <craig@craig-russell.co.uk>
# Basic Personalised Content Beacon Endpoint


import datetime as DT
import logging
from flask import Flask, request, json, make_response, abort
from models import Customer, Visitor
from werkzeug.exceptions import HTTPException, BadRequest, InternalServerError, Conflict

# Logging config
logger = logging.getLogger('APE')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler()) # Log to STDOUT for now

# The app
app = Flask(__name__, static_folder='static', static_url_path='')

# Required to ensure HTTP exception handers work in debug & test
# See: http://flask.pocoo.org/docs/0.10/api/#flask.Flask.trap_http_exception
app.config['TRAP_HTTP_EXCEPTIONS'] = True


def make_jsonp_response(payload=dict(), code=200, callback="_ape.callback"):
    """Make a jsonp response object from a payload dict"""
    # Response always returns 200 code, to ensure client can handle callback
    # Actual HTTP code sent in payload
    payload['status_code'] = code
    body = "%s(%s)" % (callback, json.dumps(payload))
    response = make_response(body, 200)
    response.headers['Content-Type'] = "application/javascript;charset=utf-8"
    logger.debug(" JSONP %s" % body)
    return response


@app.route('/beacon.js')
def beacon():

    # Get args data or defaults
    args = dict()
    args['jsonp']          = request.args.get('jsonp', "_ape.callback") # JSONP callback
    args['visitor_id']     = request.args.get('cc', "")     # The APE cookie visitor_id
    args['debug']          = request.args.get('db', "")     # Debug switch
    args['page_url']       = request.args.get('dl', "")     # Page URL
    args['referrer_url']   = request.args.get('dr', "")     # Referrer URL if set
    args['page_title']     = request.args.get('dt', "")     # Page title
    args['event']          = request.args.get('ev', "")     # Event
    args['customer_id']    = request.args.get('id', "")     # The customer account ID
    args['timestamp']      = request.args.get('ld', "")     # Event timestamp
    args['language']       = request.args.get('lg', "")     # Browser language
    args['placeholders']   = request.args.get('pc', "")     # The set of Placeholder ids on this page
    args['prefix']         = request.args.get('px', "ape")  # Placeholder class prefix
    args['screen_colour']  = request.args.get('sc', 0)      # Screen colour depth
    args['screen_height']  = request.args.get('sh', 0)      # Screen height
    args['screen_width']   = request.args.get('sw', 0)      # Screen width
    args['user_agent']     = request.args.get('ua', "")     # User Agent
    args['script_version'] = request.args.get('vr', "0.0")  # Version number of this script

    # Ensure page url and customer id are provided
    if not args['page_url']:    raise BadRequest("Bad Request: Value required for page url (dl)")
    if not args['customer_id']: raise BadRequest("Bad Request: Value required for customer id (id)")

    # Extract placeholder identifiers
    placeholders = args['placeholders'].split(' ')
    prefix = "%s-" % args['prefix']
    args['placeholder_ids'] = [c.lstrip(prefix) for c in placeholders if c.startswith(prefix)]

    # Deserialise timestamp
    try:
        args['timestamp'] = DT.datetime.utcfromtimestamp(int(args['timestamp']) / 1000)
    except ValueError:
        args['timestamp'] = DT.datetime.now()

    # Convert values to base data types
    args['screen_width']  = int(args['screen_width'])
    args['screen_height'] = int(args['screen_height'])
    args['screen_colour'] = int(args['screen_colour'])
    args['debug']         = (args['debug'] == "true")

    # The response payload
    payload = dict()

    # Respect Do Not Track
    if request.headers.get('DNT', False):
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

            # Ensure we have placeholder ids (hence there are ads on the page)
            if args['placeholder_ids']:

                # Get personalised components for this visitor for these placeholders
                components = visitor.components(ad_ids=args['placeholder_ids'])
                
                # Format components for json response
                payload['components'] = dict()
                for component in components:
                    key = "%s-%s" % (args['prefix'], component.id)
                    payload['components'][key] = dict()
                    payload['components'][key]['id']      = component.id
                    payload['components'][key]['styles']  = component.styles
                    payload['components'][key]['content'] = component.content
    
    return make_jsonp_response(payload, callback=args['jsonp'])


@app.errorhandler(HTTPException)
def handle_error(e):
    logger.error("HTTPException %s %s %s" % (e.code, e.name, e.description))
    return make_jsonp_response(dict(description=e.description, name=e.name), e.code)


@app.errorhandler(Exception)
def handle_error(e):
    logger.error("Exception %s %s" % (e.__class__.__name__, e.message))
    e = InternalServerError()
    return make_jsonp_response(dict(description=e.description, name=e.name), e.code)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)