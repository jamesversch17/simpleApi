from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import os.path
from os import path

# initialization of app
app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# set up the Model
class ChessModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	piece = db.Column(db.String(100), nullable=False)
	start_sq = db.Column(db.String(10), nullable=False)
	end_sq = db.Column(db.String(10), nullable=False)
	capture = db.Column(db.Boolean, nullable=False)

	def __repr__(self):
		return f"Move(piece = {piece}, start_sq = {start_sq}, end_sq = {end_sq}, capture = {capture})"

if path.exists('database.db') is False:
	db.create_all()

# organize the database entries
resource_fields = {
	'id': fields.Integer,
	'piece': fields.String,
	'start_sq': fields.String,
	'end_sq': fields.String,
	'capture': fields.Boolean
}

# creation of the move resource
class Move(Resource):

	# function that returns info from a specific move
	@marshal_with(resource_fields)
	def get(self, move_number):
		result = ChessModel.query.filter_by(id=move_number).first()
		if not result:
			abort(404, message="Could not find move with that id")
		return result

	# function that enters the move into the database
	@marshal_with(resource_fields)
	def put(self, move_number):

		# parse the given data
		put_move_args = reqparse.RequestParser()
		put_move_args.add_argument("piece", type=str, help="piece moved", required=True)
		put_move_args.add_argument("start_sq", type=str, help="start_sq", required=True)
		put_move_args.add_argument("end_sq", type=str, help="end_sq", required=True)
		put_move_args.add_argument("capture", type=bool, help="capture", required=True)
		
		args = put_move_args.parse_args()
	
		# search to see if the id is already taken
		result = ChessModel.query.filter_by(id=move_number).first()
		if result:
			abort(409, message="move id taken...")

		# create the move and add it to the database
		move = ChessModel(id=move_number, piece=args['piece'], start_sq=args['start_sq'], end_sq=args['end_sq'], capture=args['capture'])
		db.session.add(move)
		db.session.commit()
		return move, 201

	# function to enter previous entries to the database
	@marshal_with(resource_fields)
	def patch(self, move_number):

		# parse the data given for the update
		update_move_args = reqparse.RequestParser()
		update_move_args.add_argument("piece", type=str, help="piece moved")
		update_move_args.add_argument("start_sq", type=str, help="start_sq")
		update_move_args.add_argument("end_sq", type=str, help="end_sq")
		update_move_args.add_argument("capture", type=bool, help="capture")

		args = update_move_args.parse_args()

		# check to see if the database contains the move the user wants to update
		result = ChessModel.query.filter_by(id=move_number).first()
		if not result:
			abort(404, message="move doesn't exist, cannot update")

		# see what data is updated
		if args['piece']:
			result.piece = args['piece']
		if args['start_sq']:
			result.start_sq = args['start_sq']
		if args['end_sq']:
			result.end_sq = args['end_sq']
		if args['capture']:
			result.capture = args['capture']

		# update the database
		db.session.commit()

		return result

# add the resource to the api
api.add_resource(Move, "/move/<int:move_number>")

if __name__ == "__main__":
	app.run(debug=True)
