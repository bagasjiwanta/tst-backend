from flask_restful import Resource, reqparse
from database.dbmanager import query
from src.auth import authorize
from src.utils import res
import sqlite3

class Store(Resource):

    def get(self):
        # auth
        user = authorize()
        
        # select stores and return
        stores = query('select id, name from stores where user_id = ?', (user['id'], ))
        print(stores)
        for i in range(len(stores)):
            id, name = stores[i]
            stores[i] = {
                'id': id, 'name': name
            }
        return stores
            

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
        if check_count[0] >= 5:
            return res("users can only have 5 maximum store", 400)
        
        # creating store
        try:
            insertion = query('insert into stores (name, user_id) values(?, ?)', (args['name'], user['id']), read=False)
            return res("store created with id = " + str(insertion))

        except sqlite3.Error:
            return res("failed creating new store", 500)
        

    def delete(self):
        # auth
        user = authorize()

        # args
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('id', type=str, required=True)
        args = parser.parse_args()
        
        # delete store
        query('delete from stores where user_id = ? and id = ?', (user['id'], args['id']), read=False)

        # To do : delete products associated with this store
        
        # To do : delete categories associated with this store

        return res("store deleted")
