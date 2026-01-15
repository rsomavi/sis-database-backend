from quart import request

import re
import uuid
import os

from db import user_exists

# ahora tiene un poco las globales y funciones varias
PORT = os.environ["PORT"]
SECRET_UUID = uuid.UUID(os.environ["SECRET_UUID"])
# DB_URL = f'postgresql+asyncpg://{os.environ["DB_USER"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}'

async def identify_user() -> tuple[str, str, int]:
	"""	devuelve un tupla de:
		uuid de user o None si falla
		None o una string de error si falla
		el numero de status
	"""
	token = request.headers.get("Authorization")
	if not token:
		return None, "token requerido", 401
	
	if not token.startswith("Bearer "):
		return None, "token invalido (Bearer)", 400

	token = token[7:]
	matches = re.match(r"^([a-f\d-]{36})\.([a-f\d]{17})$", token)
	if not matches:
		return None, "bad login token (no cumple regex)", 400

	user_uuid, user_hash = matches.groups()
	if apply_hash(user_uuid) != user_hash:
		return None, "bad login token (no cumple el hash)", 400

	if not await user_exists(user_uuid):
		return None, "bad login token (el usuario ya no existe)", 400

	return user_uuid, "", 200

def apply_hash(uid: str) -> str:
	user_hash = str(uuid.uuid5(SECRET_UUID, uid))
	return user_hash[:8] + user_hash[-9:]