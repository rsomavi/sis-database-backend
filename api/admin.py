from quart import Blueprint, jsonify, request
from db import *
from utils import identify_user

admin = Blueprint("admin", __name__)

# CRUD PARA LAS PELICULAS

@admin.route("/movie", methods=["POST"])
async def crud_create_movie():
	data = await request.get_json(silent=True, force=True) or {}
	user_uuid, err_msg, st = await identify_user()

	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if not await is_admin(user_uuid):
		return jsonify({"error": "no tienes autorizacion"}), 403
	
	j, st = await create_movie(data)
	return jsonify(j), st


@admin.route("/movie", methods=["PUT"])
async def crud_replace_movie():
	data = await request.get_json(silent=True, force=True) or {}
	user_uuid, err_msg, st = await identify_user()

	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if not await is_admin(user_uuid):
		return jsonify({"error": "no tienes autorizacion"}), 403

	j, st = await replace_movie(data)

	return jsonify(j), st


# @admin.route("/movie", methods=["PATCH"])
# async def update_movie():
# 	data = await request.get_json(silent=True, force=True) or {}
# 	user_uuid, err_msg, st = await identify_user()

# 	if not user_uuid:
# 		return jsonify({"error": err_msg}), st

# 	if not await is_admin(user_uuid):
# 		return jsonify({"error": "no tienes autorizacion"}), 403

# 	return jsonify(j), st

@admin.route("/movie", methods=["DELETE"])
async def crud_delete_movie():
	data = await request.get_json(silent=True, force=True) or {}
	user_uuid, err_msg, st = await identify_user()

	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if not await is_admin(user_uuid):
		return jsonify({"error": "no tienes autorizacion"}), 403

	j, st = await delete_movie(data.get("movieid", -1))
	return jsonify(j), st

@admin.route("/user/<uuid:user_uuid>", methods=["PUT"])
async def set_client_discount(user_uuid):
	data = await request.get_json(silent=True, force=True) or {}
	admin_uuid, err_msg, st = await identify_user()

	if not admin_uuid:
		return jsonify({"error": err_msg}), st

	if not await is_admin(admin_uuid):
		return jsonify({"error": "no tienes autorizacion"}), 403

	j, st = await client_discount(str(user_uuid), data.get("discount", -1))
	return jsonify(j), st


# NUEVOS ENDPOINTS

@admin.route("/clientesSinPedidos", methods=["GET"])
async def get_clientes_sin_pedidos():
	user_uuid, err_msg, st = await identify_user()

	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if not await is_admin(user_uuid):
		return jsonify({"error": "no tienes autorizacion"}), 403
	
	j, st = await fetch_clientes_sin_pedidos()

	return jsonify(j), st

@admin.route("/estadisticaVentas/<year>/<country>", methods=["GET"])
async def get_estadisticas(year, country):
	# TODO: DESCOMENTAR ANTES DE TERMINAR
	user_uuid, err_msg, st = await identify_user()

	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if not await is_admin(user_uuid):
		return jsonify({"error": "no tienes autorizacion"}), 403

	if year != "all":
		try:
			year = int(year)

			if year < 2000:
				return jsonify({"error": "el year tiene un valor invalido"}), 400
		except:
			return jsonify({"error": "el year tiene que ser o numero o all"}), 400
	

	j, st = await fetch_stats(year, country)

	return jsonify(j), st

@admin.route("/testDeadlock/<int:i>", methods=["GET"])
async def test_deadlock(i):
	user_uuid, err_msg, st = await identify_user()

	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if not await is_admin(user_uuid):
		return jsonify({"error": "no tienes autorizacion"}), 403

	await force_deadlock(i)
	return {"message": "ok"}, 200


# EJERCICIOS DE TRANSACCIONES

@admin.route("/cascadeOff", methods=["POST"])
async def cascadeOff():
	user_uuid, err_msg, st = await identify_user()

	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if not await is_admin(user_uuid):
		return jsonify({"error": "no tienes autorizacion"}), 403
	
	await remove_on_cascade()
	return {"message": "ok"}, 200

@admin.route("/cascadeOn", methods=["POST"])
async def cascadeOn():
	user_uuid, err_msg, st = await identify_user()

	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if not await is_admin(user_uuid):
		return jsonify({"error": "no tienes autorizacion"}), 403
	
	await add_on_cascade()
	return {"message": "ok"}, 200


@admin.route("/borraPais/<country>", methods=["DELETE"])
async def remove_users_1(country):
	user_uuid, err_msg, st = await identify_user()

	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if not await is_admin(user_uuid):
		return jsonify({"error": "no tienes autorizacion"}), 403

	j, st = await delete_clients_from(country)

	return jsonify(j), st

@admin.route("/borraPaisIncorrecto/<country>", methods=["DELETE"])
async def remove_users_2(country):
	user_uuid, err_msg, st = await identify_user()

	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if not await is_admin(user_uuid):
		return jsonify({"error": "no tienes autorizacion"}), 403

	j, st = await delete_clients_error_from(country)

	return jsonify(j), st


@admin.route("/borraPaisIntermedio/<country>", methods=["DELETE"])
async def remove_users_3(country):
	user_uuid, err_msg, st = await identify_user()

	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if not await is_admin(user_uuid):
		return jsonify({"error": "no tienes autorizacion"}), 403

	j, st = await delete_clients_intermedio_from(country)

	return jsonify(j), st

