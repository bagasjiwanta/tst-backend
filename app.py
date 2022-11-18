# Setups
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from dbmanager import query
from utils import get_hash, encode_token, authorize
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
api = Api(app)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# /users
signup_parser = reqparse.RequestParser(bundle_errors=True)
signup_parser.add_argument('email', type=str, required=True)
signup_parser.add_argument('password', type=str, required=True)
signup_parser.add_argument('name', type=str, required=True)

@app.route('/users/signup', methods=['POST'])
def signup():
    args = signup_parser.parse_args()
    check_user = query('select * from users where email = ?', [args['email']], one=True)
    if check_user is not None:
        return "user already exists", 400
    
    password = get_hash(args['password'])
    sql = "insert into users (email, password, name) values(?, ?, ?)"
    variables = (args['email'], password, args['name'])
    print(variables)
    insert_id = query(sql, variables, read=False)
    if insert_id is None:
        return "failed creating user", 400

    return "signup success", 200
    
signin_parser = reqparse.RequestParser(bundle_errors=True)
signin_parser.add_argument('email', type=str)
signin_parser.add_argument('password', type=str)
signin_parser.add_argument('token', type=str)


@app.route('/users/signin', methods=['POST'])
def signin():
    args = signin_parser.parse_args()
    check_user = query('select * from users where email = ?', [args['email']], one=True)
    if check_user is None:
        return "user with email " + args['email'] + " does not exists", 400

    hashed = get_hash(args['password'])
    _id, email, name, password = check_user

    if hashed == password:
        token = encode_token(email, name)
        return token, 200

# /store
class Store(Resource):
    def get(self):
        return 1
    def post(self):
        return 1
    def delete(self):
        return 1

if __name__ == '__main__':
    app.run(debug=True)