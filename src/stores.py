from flask_restful import Resource, reqparse
from database.dbmanager import query, init_store_db
from src.auth import authorize
from src.utils import res
import sqlite3
import os

class Store(Resource):

    user_store_max = 2

    def get(self):
        # auth
        user = authorize()
        
        # select stores and return
        stores = query('select id, name from stores where user_id = ?', (user['id'], ))
        for i in range(len(stores)):
            id, name = stores[i]
            stores[i] = {
                'id': id, 'name': name
            }
        return res(data=stores)
            

    def post(self):
        # auth
        user = authorize()

        # args
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('name', type=str, required=True)
        args = parser.parse_args()

        # check if store already exists
        check_store = query('select * from stores where name = ? and user_id = ?', (args['name'], user['id']), one=True)
        if check_store is not None:
            return res("store already exist", 400)

        # check if store count is more than max
        check_count = query('select count(*) from stores where user_id = ?', (user['id'], ), one=True)
        if check_count[0] >= self.user_store_max:
            return res("users can only have " + str(self.user_store_max) + " maximum store", 400)
        
        # creating store
        try:
            lastid = query('insert into stores (name, user_id) values(?, ?)', (args['name'], user['id']), type="insert")
            init_store_db(lastid)
            return res("store created with id = " + str(lastid))

        except sqlite3.Error as e:
            print(e)
            return res("failed creating new store", 500)
        

    def delete(self):
        # auth
        user = authorize()

        # args
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('id', type=str, required=True)
        args = parser.parse_args()
        
        # delete store
        store_name = query('select name from stores where user_id = ? and id = ?', (user['id'], args['id']), one=True)
        if store_name is None:
            return res('store not found', 404)
        query('delete from stores where user_id = ? and id = ?', (user['id'], args['id']), type="delete")

        db_exists = os.path.isfile('database/store/' + str(args['id']) + '.db')
        if db_exists:
            os.remove('database/store/' + str(args['id']) + '.db')
            

        # To do : delete products associated with this store
        
        # To do : delete categories associated with this store

        return res("store '" + store_name[0]  + "' deleted")
