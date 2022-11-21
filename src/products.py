from flask_restful import Resource, reqparse
from src.utils import res
from src.auth import authorize
from database.dbmanager import query

class Product(Resource):
    
    def sort_str_to_query(sort='name', order="asc") -> str | None:
        if order != "asc" and order != "desc":
            order = None
        
        if sort != 'name' and sort != 'stock' and sort != 'code' and sort != 'buy_price' and sort != 'sell_price' and sort != 'category':
            sort = None

        if order is None or sort is None:
            return None
        
        return sort + " " + order


    def get(self, store_id):
        authorize()
        # filter -> sort -> search
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('keyword', type=str)
        parser.add_argument('sort', type=list[dict[str, str]])
        parser.add_argument('filter', type=dict)
        parser.add_argument('full_search', type=bool)
        parser.add_argument('highlight', type=bool)
        args = parser.parse_args()

        # todo
        prefix = """
        select p.code code, p.name name, p.description description, p.stock stock, p.buy_price buy_price,
        p.sell_price sell_price, c.name category
        from products p inner join categories c on p.category_id = c.id 
        """

        if 'full_search' in args and args['full_search'] is True:
            sql = """
                CREATE VIRTUAL TABLE productsearch
                USING FTS5(pname, pdescription, pcode, cname); 
            """

        if args['sort'] is not None:
            sorter = []
            for i in range(len(args['sort'])):
                for sort, order in args['sort'][i].items():
                    sort_str = Product.sort_str_to_query(sort, order)
                    if sort_str is not None:
                        sorter.append(sort_str)
        
        if 'search' in args:
            pass

        data = query('select * from products limit 10', store=True, store_id=store_id)
        for i in range(len(data)):
            id, name, description, stock, unit, buy_price, sell_price, minimum_stock, category_id = data[i]
            data[i] = {
                'id': id,
                'name': name,
                'description': description,
                'stock': stock,
                'unit': unit,
                'buy_price' : buy_price,
                'sell_price' : sell_price,
                'minimum_stock': minimum_stock,
                'category_id': category_id
            } 

        return res(data=data)

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

        