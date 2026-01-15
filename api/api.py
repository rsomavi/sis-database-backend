from utils import identify_user, PORT
from quart import Quart, jsonify, request

from admin import admin # para los endpoints de admin

import math
from datetime import datetime

from dotenv import load_dotenv
from db import *

load_dotenv()
api = Quart(__name__)

# def pretty_jsonify(data):
# 	return api.response_class(
#         response=json.dumps(data, indent=4, ensure_ascii=False),
#         status=200,
#         mimetype="application/json"
#     )

@api.route("/movies", methods=["GET"])
async def get_movies():
	# data = await request.get_json(silent=True, force=True) or {}
	data = request.args
	args = {**data}
	user_uuid, err_msg, st = await identify_user()

	if not user_uuid:
		return jsonify({"error": err_msg}), st

	# if data.get("date") and not re.match(r"(\d{4})(-|/)?(0[1-9]|1[0-2])(-|/)?(0[1-9]|[12][0-9]|3[01])", data.get("date")):
	# 	return jsonify({"error": "date invalida"}), 400
	if data.get("date"):
		d = None
		for formato in ["%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y"]:
			try:
				d = datetime.strptime(data.get("date"), formato).date()
				break
			except ValueError:
				continue

		if not d:
			return jsonify({"error": "date invalida"}), 400

		args["date"] = d


	if data.get("year"):
		try:
			args["year"] = int(data["year"])
		except:
			return jsonify({"error": "year tiene que ser un int"}), 400

	if data.get("max_price"):
		try:
			args["max_price"] = round(float(data["max_price"]), 2)
		except:
			return jsonify({"error": "max_price tiene que ser un int o float"}), 400
		# data["price"] = round(data["price"], 2)

	# if data.get("title") and type(data.get("title")) != str:
	# 	return jsonify({"error": "title tiene que ser una string"}), 400
	
	# if data.get("genre") and type(data.get("genre")) != str:
	# 	return jsonify({"error": "genre tiene que ser una string"}), 400

	if data.get("limit") and type(data.get("limit")) != int:
		try:
			args["limit"] = int(data["limit"])
		except: 
			return jsonify({"error": "limit tiene que ser un int"}), 400
	
	if args.get("limit", 0) < 0 or args.get("max_price", 0) < 0 or args.get("year", 1900) < 1900:
		return jsonify({"error": "algun numero tiene un valor invalido"}), 400

	# if data.get("actor") and type(data.get("actor")) != str:
	# 	return jsonify({"error": "el actor tiene que ser una string"}), 400

	params = {k: args.get(k) for k in ["date", "title", "year", "genre", "max_price", "limit", "actor"] if k in args}
	movies = await fetch_movies(params)

	return jsonify(movies), 200


@api.route("/movies/<int:movie_id>", methods=["GET"])
async def get_movie_by_id(movie_id):
	user_uuid, err_msg, st = await identify_user()

	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if movie_id <= 0:
		return jsonify({"error": "pelicula invalida"}), 400

	movie = await fetch_movie_id(movie_id)
	if not movie:
		return jsonify({"error": "pelicula no encontrada"}), 404

	return jsonify(movie), 200

@api.route("/cart", methods=["GET"])
async def see_cart():
	user_uuid, err_msg, st = await identify_user()

	if not user_uuid:
		return jsonify({"error": err_msg}), st

	movies = await fetch_cart(user_uuid)
	return jsonify(movies), 200


@api.route("/cart/<int:movie_id>", methods=["PUT"])
async def add_to_cart(movie_id):
	user_uuid, err_msg, st = await identify_user()

	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if movie_id <= 0:
		return jsonify({"error": "pelicula invalida"}), 400

	j, st = await handle_cart_addition(user_uuid, movie_id)
	return jsonify(j), st

@api.route("/cart/<int:movie_id>", methods=["DELETE"])
async def remove_from_cart(movie_id):
	user_uuid, err_msg, st = await identify_user()

	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if movie_id <= 0:
		return jsonify({"error": "pelicula invalida"}), 400

	if not await handle_cart_removal(user_uuid, movie_id):
		return jsonify({"error": "pelicula no esta en el carrito"}), 404
	
	return jsonify({"message": "pelicula eliminada correctamente"}), 200


@api.route("/cart/checkout", methods=["POST"])
async def checkout():
	user_uuid, err_msg, st = await identify_user()
	
	if not user_uuid:
		return jsonify({"error": err_msg}), st

	j, st = await close_cart(user_uuid)
	return jsonify(j), st

@api.route("/user/credit", methods=["GET"])
async def get_credit():
	user_uuid, err_msg, st = await identify_user()
	
	if not user_uuid:
		return jsonify({"error": err_msg}), st

	j, st = await fetch_balance(user_uuid)
	return jsonify(j), st

@api.route("/user/credit", methods=["POST"])
async def update_credit():
	data = await request.get_json(silent=True, force=True) or {}
	user_uuid, err_msg, st = await identify_user()
	
	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if not data.get("amount"):
		return jsonify({"error": "el cuerpo debe tener '{\"amount\": float}"}), 400

	if type(data.get("amount")) not in [float, int]:
		return jsonify({"error": "el cuerpo debe tener '{\"amount\": float}"}), 400

	amount = math.floor(data.get("amount") * 100) / 100
	if amount <= 0 or amount > 9999999:
		return jsonify({"error": "valor invalido para el balance"}), 400

	j, st = await update_balance(user_uuid, amount)
	return jsonify(j), st

@api.route("/orders/<int:order_id>", methods=["GET"])
async def see_order(order_id):
	user_uuid, err_msg, st = await identify_user()
	
	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if order_id <= 0:
		return jsonify({"error": "id de orden invalido"}), 400

	j, st = await fetch_order(user_uuid, order_id)
	return jsonify(j), st

@api.route("/vote/<int:movie_id>", methods=["PUT"])
async def vote_movie(movie_id):
	data = await request.get_json(silent=True, force=True) or {}
	user_uuid, err_msg, st = await identify_user()
	
	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if movie_id <= 0:
		return jsonify({"error": "id de pelicula invalida"}), 400

	if data.get("rating", None) is None:
		return jsonify({"error": "la valoracion tiene que tener almenos un rating"}), 400
	
	rating = data.get("rating")
	msg = data.get("comment")

	if type(rating) not in [float, int]:
		return jsonify({"error": "la valoracion debe ser un numero"}), 400

	if rating > 5 or rating < 0:
		return jsonify({"error": "la valoracion invalida"}), 400

	rating = math.floor(rating*10)/10

	if msg and type(msg) != str:
		return jsonify({"error": "la comentario invalido"}), 400

	j, st = await put_movie_vote(user_uuid, movie_id, rating, msg)
	return jsonify(j), st

@api.route("/vote/<int:movie_id>", methods=["DELETE"])
async def remove_vote(movie_id):
	user_uuid, err_msg, st = await identify_user()
	
	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if movie_id <= 0:
		return jsonify({"error": "id de pelicula invalida"}), 400

	j, st = await delete_movie_vote(user_uuid, movie_id)
	return jsonify(j), st


@api.route("/user/<uuid:target_uuid>/votes", methods=["GET"])
async def see_user_votes(target_uuid):
	user_uuid, err_msg, st = await identify_user()
	
	if not user_uuid:
		return jsonify({"error": err_msg}), st

	j, st = await fetch_client_votes(target_uuid)
	# print(j)
	return jsonify(j), st

@api.route("/user", methods=["GET"])
async def see_self_info():
	user_uuid, err_msg, st = await identify_user()

	if not user_uuid:
		return jsonify({"error": err_msg}), st
	
	j, st = await fetch_client_info(user_uuid)
	return jsonify(j), st


if __name__ == '__main__':
	api.register_blueprint(admin)
	api.run(host='0.0.0.0', port=PORT)