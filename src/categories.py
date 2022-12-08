from flask_restful import Resource, reqparse
from database.dbmanager import query
from flask import abort
from src.utils import res
from src.auth import authorize

class Category(Resource):

    def check_store_owner(self, store_id, user_id):
        owner = query('select user_id from stores where id = ?', (store_id, ), one=True)
        if owner[0] != int(user_id):
            abort(403, "you are not the store owner")

    def get(self, store_id):
        # auth
        user = authorize()

        # check store owner
        self.check_store_owner(store_id, user['id'])
        
        # get categories
        categories = query('select id, name from categories', store=True, store_id=store_id)
        for i in range(len(categories)):
            id, name = categories[i]
            categories[i] = {
                'id': id, 'name': name
            }
        return res(data = categories)
    
    def post(self, store_id):
        # auth
        user = authorize()
        
        # check store owner
        self.check_store_owner(store_id, user['id'])

        # args
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('name', type=str, required=True)
        args = parser.parse_args()

        # insert categories

        lastrowid = query("insert into categories (name) values(?)", (args['name'], ), type="insert", 
            store=True, store_id=store_id)
        print(lastrowid)
        if lastrowid == 0:
            abort(500, 'insert error')
        return res()

    def delete(self, store_id):
        # auth
        user = authorize()
        # check store owner
        self.check_store_owner(store_id, user['id'])

        # args
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('id', type=int, required=True)
        args = parser.parse_args()

        affected = query('delete from categories where id = ?', 
            (args['id'], ), type="delete", store=True, store_id=store_id)
        if affected == 0:
            return res("delete error", 500)
        return res()

