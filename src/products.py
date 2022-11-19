from flask_restful import Resource, reqparse
from src.utils import res

class Products(Resource):
	
	def get(self):
		parser = reqparse.RequestParser(bundle_errors=True)
		parser.add_argument('keyword', type=str)
		parser.add_argument('sort', type=dict)
		parser.add_argument('filter', type=dict)
		return res()
	 

