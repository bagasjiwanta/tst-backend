from flask import Response

# generalize response object
def res(message="success", code=200, data=None ):
    ret = {
        "message" : message
    }
    if data is not None:
        ret['data'] = data
    response = (ret, code, {
        'Access-Control-Allow-Origin' : '*'
    })
    return response

