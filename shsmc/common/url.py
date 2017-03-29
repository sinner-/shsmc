import requests

def post(url, data):
    """ HTTP POST to URL wrapper.
    """

    headers = {'Content-Type': 'application/json'}
    resp = requests.post(url, headers=headers, data=data)

    return resp.text
