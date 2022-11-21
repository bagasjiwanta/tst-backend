# Setups
from flask import Flask, g
from flask_restful import Api
from database.dbmanager import  get_db
from dotenv import load_dotenv
from src.stores import Store
from src.auth import Signin, Signup
from src.categories import Category
from src.products import Product
load_dotenv()

app = Flask(__name__)
api = Api(app)

@app.route("/")
def greet():
    return """
<div>
<h1>Welcome to Product Management API</h1>
<h3> See <a href="https://docs.google.com/document/d/1jY5fNt736Rux6QwNjj-QJZ2OrJq1gOgEvFjUsfngLCs"> documentation </a> </h3>
</div>
    """

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
api.add_resource(Product, '/store/<int:store_id>/products')
api.add_resource(Signin, '/signin')
api.add_resource(Signup, '/signup')

# main process
if __name__ == '__main__':
    app.run(debug=True)