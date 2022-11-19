from flask_restful import Resource, reqparse
from database.dbmanager import queryc
from flask import abort
from src.utils import res
from src.auth import authorize

class Category(Resource):

    def check_store_owner(self, store_id, user_id):
        owner = queryc('select user_id from stores where id = ?', (store_id, ), one=True)
        if owner[0] != user_id:
            abort(403, "you are not the store owner")

    def get(self, store_id):
        # auth
        user = authorize()

        # check store owner
        self.check_store_owner(store_id, user['id'])
        
        # get categories
        categories = queryc('select id, name, description from categories where store_id = ?', (store_id, ))
        for i in range(len(categories)):
            id, name, description = categories[i]
            categories[i] = {
                'id': id, 'name': name, 'description': description
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
        parser.add_argument('description', type=str)
        args = parser.parse_args()

        # insert categories
        with_description = 'description' in args
        if with_description:
            lastrowid = queryc("insert into categories (name, description, store_id) values(?, ?, ?)", 
                (args['name'], args['description'], store_id), type="insert")
            if lastrowid == 0:
                abort(500, "insert error")
        else:
            lastrowid = queryc("insert into categories (name, store_id) values(?, ?)", (args['name'], store_id), type="insert")
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

        affected = queryc('delete from categories where store_id = ? and id = ?', 
            (store_id, args['id']), type="delete")
        if affected == 0:
            return res("delete error", 500)
        return res()

