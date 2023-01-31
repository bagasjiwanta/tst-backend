from flask_restful import Resource, reqparse
from src.utils import res
from src.auth import authorize
from database.dbmanager import query, get_store_db

class GetAllProduct(Resource):
    def get(self, store_id):
        authorize()
        data = query(
'''
select *
from products inner join categories c where products.category_id = c.id
''', store=True, store_id=store_id
            )

        for i in range(len(data)):
            id, name, description, stock, unit, buy_price, sell_price, minimum_stock, category_id, _c, category = data[i]
            data[i] = {
                'id': id,
                'name': name,
                'description': description,
                'stock': stock,
                'unit': unit,
                'buy_price' : buy_price,
                'sell_price' : sell_price,
                'minimum_stock': minimum_stock,
                'category_id': category_id,
                'category': category
            } 
        return res(data=data)

class GetProduct(Resource):
    def sort_str_to_query(sort='name', order="asc"):
        if order != "asc" and order != "desc":
            order = None
        
        if sort != 'name' and sort != 'stock' and sort != 'code' and sort != 'buy_price' and sort != 'sell_price' and sort != 'category':
            sort = None

        if order is None or sort is None:
            return None
        
        return sort + " " + order


    def post(self, store_id):
        authorize()
        # filter -> sort -> search
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('highlight', type=str, default="")
        parser.add_argument('low_stock', type=bool, default=False)
        parser.add_argument('sales', )
        args = parser.parse_args()

        if len(args['highlight']) > 0:
            print(args['highlight'])
            sql = """
drop table if exists searching;

create virtual table searching
using fts5(id, name, description, category);

insert into searching (id, name, description, category)
select p.id id, p.name name, p.description description, c.name category
from products p inner join categories c on p.category_id = c.id;
            """
            db = get_store_db(store_id)
            cursor = db.cursor()
            cursor.executescript(sql)
            db.commit()
            sql2 = """
select 
    id,
    highlight(searching, 1, '<b>', '</b>') name,
    highlight(searching, 2, '<b>', '</b>') description,
    highlight(searching, 3, '<b>', '</b>') category
from searching
where searching match ?
order by rank"""
            result = cursor.execute(sql2, (args['highlight'], )).fetchall()
            for i in range(len(result)):
                id, name, description, category = result[i]
                result[i] = {
                    'id': id,
                    'name': name,
                    'description': description,
                    'category': category
                }
            return res(data=result)
        
        elif args['low_stock']:
            low_stock = query("select low_stock_percentage from stores where id = ?", (int(store_id), ), one=True)

            data = query("""
select *
from products inner join categories c where products.category_id = c.id 
and buy_price is not null and stock <= ? * minimum_stock """, 
                store=True, 
                store_id=store_id, 
                args=(float(low_stock[0]), )
            )

            for i in range(len(data)):
                id, name, description, stock, unit, buy_price, sell_price, minimum_stock, category_id, _c, category = data[i]
                data[i] = {
                    'id': id,
                    'name': name,
                    'description': description,
                    'stock': stock,
                    'unit': unit,
                    'buy_price' : buy_price,
                    'sell_price' : sell_price,
                    'minimum_stock': minimum_stock,
                    'category_id': category_id,
                    'category': category
                } 

            return res(data=data)
        
        else:
            data = query(
'''
select *
from products inner join categories c where products.category_id = c.id
''', store=True, store_id=store_id
            )

            for i in range(len(data)):
                id, name, description, stock, unit, buy_price, sell_price, minimum_stock, category_id, _c, category = data[i]
                data[i] = {
                    'id': id,
                    'name': name,
                    'description': description,
                    'stock': stock,
                    'unit': unit,
                    'buy_price' : buy_price,
                    'sell_price' : sell_price,
                    'minimum_stock': minimum_stock,
                    'category_id': category_id,
                    'category': category
                } 
            return res(data=data)



class Product(Resource):


    def delete(self, store_id):
        authorize()
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('id', type=str, required=True)
        args = parser.parse_args()

        affected = query('delete from products where id = ?', (args['id'], ), type="delete", store=True, store_id=store_id)
        if affected == 0:
            return res(500, "delete fail")
        return res()


    def post(self, store_id):
        authorize()
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('description', type=str)
        parser.add_argument('stock', type=int)
        parser.add_argument('unit', type=str, required=True)
        parser.add_argument('buy_price', type=float)
        parser.add_argument('sell_price', type=float)
        parser.add_argument('category_id', type=int)
        parser.add_argument('minimum_stock', type=int)
        args = parser.parse_args()
        insert = []
        values = []
        questionmark = []
        for key, value in args.items():
            if value is not None:
                insert.append(key)
                values.append(value)
                questionmark.append("?")
    
        sql = "insert into products (" + ", ".join(insert) + ") values (" + ", ".join(questionmark) + ")"
        print(tuple(values))
        print(sql)
        last = query(sql, tuple(values), type="insert", store=True, store_id=store_id) 
        if last == 0:
            return res(500, "insert fail")
        
        return res()
    
    def update(self, store_id):
        authorize()
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('id', type=int, required=True)
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('description', type=str)
        parser.add_argument('stock', type=int)
        parser.add_argument('unit', type=str, required=True)
        parser.add_argument('buy_price', type=float)
        parser.add_argument('sell_price', type=float)
        parser.add_argument('category_id', type=int)
        parser.add_argument('minimum_stock', type=int)
        args = parser.parse_args()
        update = []
        values = []
        for key, value in args.items():
            if value is not None:
                update.append(key + " = ? ")
                values.append(value)
    
        values.append(args['id'])
        sql = "update products set " + ", ".join(update) + "where id = ?"
        affected = query(sql, tuple(update), type="update", store=True, store_id=store_id) 
        if affected == 0:
            return res(500, "update fail")
        
        return res()

        