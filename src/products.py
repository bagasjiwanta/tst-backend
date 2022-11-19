from flask_restful import Resource, reqparse
from src.utils import res
from database.dbmanager import query

class Products(Resource):
    
    def sort_str_to_query(sort='name', order="asc") -> str | None:
        if order != "asc" and order != "desc":
            order = None
        
        if sort != 'name' and sort != 'stock' and sort != 'code' and sort != 'buy_price' and sort != 'sell_price' and sort != 'category':
            sort = None

        if order is None or sort is None:
            return None
        
        return sort + " " + order


    def get(self):
        # filter -> sort -> search
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('keyword', type=str)
        parser.add_argument('sort', type=list[dict[str, str]])
        parser.add_argument('filter', type=dict)
        args = parser.parse_args()
        prefix = """
        select p.code code, p.name name, p.description description, p.stock stock, p.buy_price buy_price,
        p.sell_price sell_price, c.name category
        from products p inner join categories c on p.category_id = c.id 
        """

        if 'sort' in args:
            sorter = []
            for i in range(len(args['sort'])):
                for sort, order in args['sort'][i].items():
                    sort_str = Products.sort_str_to_query(sort, order)
                    if sort_str is not None:
                        sorter.append(sort_str)
            return res(", ".join(sorter))
        
        if 'search' in args:
            
            pass

        return res()
     

