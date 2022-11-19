import hashlib
import datetime
import jwt
import os
from flask import request, abort
from flask_restful import Resource, reqparse
from database.dbmanager import queryc
from src.utils import res

# for hashing password
def get_hash(string):
    if (type(string) is str):
        message = string.encode()
        return hashlib.sha256(message).hexdigest()
    else:
        return None

# Make jwt token from credentials
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

# check authorization
def authorize() -> dict[str, str]: 
    if type(request.headers.get('Authorization')) is not str:
        abort(401, 'token missing')
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
        abort(401, 'token expired')
    except jwt.InvalidTokenError:
        abort(401, 'token invalid')
    except:
        abort(401, '')


# signin route
class Signin(Resource):
    def post(self):
        # args
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        # check email
        check_user = queryc('select * from users where email = ?', [args['email']], one=True)
        if check_user is None:
            return res("user with email " + args['email'] + " does not exists", 400)

        hashed = get_hash(args['password'])
        id, email, name, password = check_user

        # check password
        if hashed == password:
            token = encode_token(id, email, name)
            return res(data=token)
        
        return res("email or password mismatch", 400)


# signup route
class Signup(Resource):
    
    def post(self):
        # args
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('name', type=str, required=True)
        args = parser.parse_args()

        # check if user already exists
        check_user = queryc('select * from users where email = ?', [args['email']], one=True)
        if check_user is not None:
            return res("user already exists", 400)

        # insert user with hashed password
        password = get_hash(args['password'])
        sql = "insert into users (email, password, name) values(?, ?, ?)"
        variables = (args['email'], password, args['name'])
        insert_id = queryc(sql, variables, type="insert")
        if insert_id is None:
            return res("failed creating user", 400)
        return res("signup success")