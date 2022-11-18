# Setups
from flask import Flask, request, g, abort
from flask_restful import Api, Resource, reqparse
from database.dbmanager import query, get_db
from src.utils import res
from src.auth import authorize 
from dotenv import load_dotenv
from src.stores import Store
from src.auth import Signin, Signup
from src.categories import Category
load_dotenv()

app = Flask(__name__)
api = Api(app)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# for rebuilding db
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('database/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        
# setup routes
api.add_resource(Store, '/store')
api.add_resource(Category, '/store/<int:store_id>/categories')
api.add_resource(Signin, '/signin')
api.add_resource(Signup, '/signup')

# main process
if __name__ == '__main__':
    app.run(debug=True)