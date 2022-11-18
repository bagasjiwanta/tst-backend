import hashlib
import datetime
import jwt
import os
from flask import request

def get_hash(string):
    if (type(string) is str):
        message = string.encode()
        return hashlib.sha256(message).hexdigest()
    else:
        return None

def encode_token(id, email, name):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=3),
            'iat': datetime.datetime.utcnow(),
            'email': email,
            'id': id,
            'name': name
        }
        return jwt.encode(
            payload,
            os.environ.get('secret')
        )
    except Exception as e:
        return e

def authorize():
    if type(request.headers.get('Authorization')) is not str:
        return 'token missing'
    bearer = request.headers.get('Authorization')
    token = bearer.split(' ')[1]
    try:
        payload = jwt.decode(token, os.environ.get('secret'), algorithms=["HS256"])
        ret = {
            'email': payload.get('email'),
            'name': payload.get('name'),
            'id': payload.get('id')
        }
        return ret
    except jwt.ExpiredSignatureError:
        return 'token expired'
    except jwt.InvalidTokenError:
        return 'token invalid'

def res(message="success", code=200, data=None ):
    ret = {
        "message" : message
    }
    if data is not None:
        ret['data'] = data
    return (ret, code)

