import requests
from flask import request, current_app
import simplejson as json

# JSONP decorator, see https://gist.github.com/1094140
from functools import wraps

JSONAPI_MIMETYPE = 'application/json'
JAVASCRIPT_MIMETYPE = 'application/javascript'

def support_jsonp(f):
    """Wraps JSONified output for JSONP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # callback = request.args.get('callback', False)    # GET only
        callback = request.values.get('callback', False)    # A CombinedMultiDict with the contents of both form and args.
        if callback:
            # content = str(callback) + '(' + str(f(*args,**kwargs).data) + ')'
            # returns dump_json output instead of Dictionary
            content = str(callback) + '(' + str(f(*args,**kwargs)) + ')'
            return current_app.response_class(content, mimetype=JAVASCRIPT_MIMETYPE)
        else:
            return f(*args, **kwargs)
    return decorated_function

