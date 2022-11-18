# generalize response object
def res(message="success", code=200, data=None ):
    ret = {
        "message" : message
    }
    if data is not None:
        ret['data'] = data
    return (ret, code)

