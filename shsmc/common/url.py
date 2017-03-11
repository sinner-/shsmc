from urllib2 import build_opener
from urllib2 import Request
from urllib2 import HTTPError

def post(url, parameters):
    ''' HTTP POST to URL wrapper.

    Should probably be replaced with requests

    Args:
        url(str)        : HTTP POST target URL.
        parameters(str) : POST parameters in JSON format.

    Returns:
        response(urllib2.response)  : HTTP response object.

    Raises:
        HTTPError   : HTTP error code returned by server.
    '''

    opener = build_opener()
    req = Request(url)
    req.add_header('Content-Type', 'application/json')
    req.data = parameters
    response = None
    try:
            response = opener.open(req).read()
    except HTTPError, e:
            print e.fp.read()

    return response
