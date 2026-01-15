from utils import identify_user, PORT
from user_handler import *

from quart import Quart, jsonify, request
from dotenv import load_dotenv

import re

load_dotenv()
users = Quart(__name__)


@users.route('/user', methods=['POST', "PUT", "GET"]) # para el cliente tiene que ser PUT
async def login_user():
	data = await request.get_json(silent=True, force=True) or {}
	# data.setdefault("name", None)
	# data.setdefault("password", None)

	name, password, country = data.get("name"), data.get("password"), data.get("country")

	if not name or not password:
		return jsonify({"error": "el cuerpo debe tener la siguiente forma: '{\"name\": \"...\", \"password\": \"...\", \"country\": optional}'"}), 400
	
	# no comprueba si hay espacios o caracteres raros pero bueno
	if type(name) != str or type(password) != str:
		return jsonify({"error": "el nombre de usuario y la password tienen que ser cadenas de texto"}), 400 

	if re.search(r"[\\\"\']", name + password):
		return jsonify({"error": "el usuario o password tienen caracteres no permitidos"}), 400

	user_uuid, token = await validate_user(name, password)

	if user_uuid and request.method.upper() == "GET":
		# el usuario ya existe, se comprueba si la contraseña es la misma para devolver uid
		if not token:
			return jsonify({"error": "password incorrecta"}), 401

	else:
		if user_uuid:
			return jsonify({"error": "nombre de usuario ya existe"}), 400

		# if request.method.upper() in ["POST", "PUT"]:
		user_uuid, token = await add_user(name, password, country)

	# parece que quiere que se devuelva token solo cuando es GET y username cuando es PUT
	# get crea usuario, put valida al usuario devolviendo token
	return jsonify({"uid": user_uuid, "token": token, "username": name}), 200

@users.route('/user', methods=['PATCH'])
async def change_password():
	data = await request.get_json(silent=True, force=True) or {}
	user_uuid, err_msg, st = await identify_user()
	
	if not user_uuid:
		return jsonify({"error": err_msg}), st

	if not data.get("password"):
		return jsonify({"error": "el cuerpo tiene que ser de la forma: '{\"password\": \"...\"}'"}), 400

	if type(data["password"]) != str:
		return jsonify({"error": "la password tiene que ser una cadena de texto"}), 400

	if re.search(r"[\\\"\']", data["password"]):
		return jsonify({"error": "caracteres no permitidos"}), 400

	await update_user(user_uuid, data["password"])
	return jsonify({"message": "password actualizada"}), 200

@users.route('/user/<uuid:user_uuid>', methods=["DELETE"])
async def remove_user(user_uuid):
	admin_uuid, err_msg, st = await identify_user()

	if not admin_uuid:
		return jsonify({"error": err_msg}), st

	j, st = await delete_user(admin_uuid, user_uuid)
	return jsonify(j), st

if __name__ == '__main__':
	users.run(host='0.0.0.0', port=PORT)