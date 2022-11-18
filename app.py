# Setups
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from dbmanager import query, get_db
from utils import get_hash, encode_token, authorize, res
from dotenv import load_dotenv
import sqlite3
load_dotenv()

app = Flask(__name__)
api = Api(app)

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('database.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# /users

@app.route('/users/signup', methods=['POST'])
def signup():
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('email', type=str, required=True)
    parser.add_argument('password', type=str, required=True)
    parser.add_argument('name', type=str, required=True)
    args = parser.parse_args()

    check_user = query('select * from users where email = ?', [args['email']], one=True)
    if check_user is not None:
        return res("user already exists", 400)

    password = get_hash(args['password'])
    sql = "insert into users (email, password, name) values(?, ?, ?)"
    variables = (args['email'], password, args['name'])
    insert_id = query(sql, variables, read=False)
    if insert_id is None:
        return res("failed creating user", 400)
    return res("signup success")


@app.route('/users/signin', methods=['POST'])
def signin():
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('email', type=str, required=True)
    parser.add_argument('password', type=str, required=True)
    args = parser.parse_args()
    check_user = query('select * from users where email = ?', [args['email']], one=True)
    if check_user is None:
        return res("user with email " + args['email'] + " does not exists", 400)

    hashed = get_hash(args['password'])
    id, email, name, password = check_user

    if hashed == password:
        token = encode_token(id, email, name)
        return res(data=token)
    
    return res("email or password mismatch", 400)

# /store
class Store(Resource):
    def get(self):
        user = authorize()
        if type(user) == str:
            return res("Unauthorized, " + user, 401)
        
        stores = query('select id, name from store where user_id = ?', (user['id'], ))
        print(stores)
        for i in range(len(stores)):
            id, name = stores[i]
            stores[i] = {
                'id': id, 'name': name
            }
        return stores
            
    def post(self):
        user = authorize()
        if type(user) == str:
            return res("Unauthorized, " + user, 401)
        print(user['id'])
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('name', type=str, required=True)
        args = parser.parse_args()
        check_store = query('select * from store where name = ? and user_id = ?', (args['name'], user['id']), one=True)
        if check_store is not None:
            return res("store already exist", 400)

        check_count = query('select count(*) from store where user_id = ?', (user['id'], ), one=True)
        if check_count[0] >= 5:
            return res("users can only have 5 maximum store", 400)
        
        try:
            insertion = query('insert into store (name, user_id) values(?, ?)', (args['name'], user['id']), read=False)
            return res("store created with id = " + str(insertion))

        except sqlite3.Error:
            return res("failed creating new store", 500)
        
    def delete(self):
        user = authorize()
        if type(user) == str:
            return res("Unauthorized" + user, 401)
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('id', type=str)
        parser.add_argument('name', type=str)
        args = parser.parse_args()
        if 'id' not in args and 'name' not in args:
            return res("incomplete parameters", 401)
        
        if 'id' in args:
            deletion = query('delete from store where user_id = ? and id = ?', (user['id'], args['id']), read=False)
            print(deletion)

        if 'name' in args:
            deletion = query('delete from store where user_id = ? and name = ?', (user['id'], args['name']), read=False)
            print(deletion)
        
        return res("store deleted")
        
api.add_resource(Store, '/store')

if __name__ == '__main__':
    app.run(debug=True)