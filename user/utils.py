from quart import request

from argon2 import PasswordHasher

import re
import uuid
import os

from db import async_session, Client
from sqlalchemy import select

# ahora tiene un poco las globales y funciones varias

PORT = os.environ["PORT"]
SECRET_UUID = uuid.UUID(os.environ["SECRET_UUID"])

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
		return None, "bad share token (no cumple regex)", 400

	user_uuid, user_hash = matches.groups()
	if apply_hash(user_uuid) != user_hash:
		return None, "bad share token (no cumple el hash)", 400

	if not await user_exists(user_uuid):
		return None, "bad login token (el usuario ya no existe)", 400

	return user_uuid, "", 200

def apply_hash(uid: str) -> str:
	# al hacer el uuid5 ya estamos aplicando sha-1, https://en.wikipedia.org/wiki/Universally_unique_identifier#Versions_3_and_5_(namespace_name-based)
	# lo que pasa es que luego lo pasa al formato estadar de uuid:
	# xxxxxxxx-xxxx-5xxx-Nxxx-xxxxxxxxxxxx - 5 porque es uuid5 y la N la variante
	# para acortar nuestro hash vamos a coger los primeros 8 y los últimos 9

	# se reduce la entropia pero tampoco pasa nada, asi tambien tenemos un token (determinista) mas corto
	# y lo de [:8] [-9:] le da una vuelta mas de complejidad al hash (tampoco muchisima)
	# al y se quiere sacar con fuerza bruta con 17 caracteres de longitud sigue siendo muy complicado

	user_hash = str(uuid.uuid5(SECRET_UUID, uid))
	return user_hash[:8] + user_hash[-9:]


async def user_exists(user_uuid: str) -> bool:
	async with async_session() as s:
		result = await s.execute(select(Client).where(Client.uuid == user_uuid))
		exists = result.scalars().first() is not None

		return exists 


_ph = PasswordHasher()

# el pepper es un extra para el hash de la contraseña, tampoco muy importante
def hash_password(password: str) -> str:
	return _ph.hash(password.encode("utf-8"))

def check_password(password_hash: str, password: str) -> bool:
	try:
		_ph.verify(password_hash, password.encode("utf-8"))
	except:
		return False

	return True 