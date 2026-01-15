from utils import apply_hash, hash_password, check_password
from db import async_session, Client
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError

import uuid

""" FUNCIONES DE GESTION DE USUARIOS"""


async def add_user(username: str, password: str, country: str = None) -> tuple[str, str]:
	""" devuelve el user uuid como string y el token de acceso """

	new_client = Client(username=username, uuid=uuid.uuid4(), password=hash_password(password), country=country)

	async with async_session() as s:
		# por si hay colision y se genera el mismo uuid (muy muy muy muy myu improbable)
		while True:
			try:
				s.add(new_client)
				await s.commit()
				break
			except IntegrityError:
				await s.rollback()

	return str(new_client.uuid), str(new_client.uuid) + "." + apply_hash(str(new_client.uuid))

async def update_user(user_uuid: str, password: str):
	async with async_session() as s:
		result = await s.execute(select(Client).where(Client.uuid == user_uuid))
		user = result.scalars().first()
		
		user.password = hash_password(password)
		await s.commit()
		
async def delete_user(admin_uuid: str, user_uuid: str) -> tuple[dict[str, str], int]:
	async with async_session() as s:
		result = await s.execute(select(Client).where(Client.uuid == admin_uuid))
		admin = result.scalars().first()

		if admin.role != "admin":
			return {"error": "no tienes autorizacion"}, 403
		

		result = await s.execute(delete(Client).where(Client.uuid == user_uuid))
		await s.commit()

		if result.rowcount == 0:
			return {"error": f"usuario con uuid '{user_uuid}' no encontrado"}, 404
		
		return {"message": "usuario borrado con exito"}, 200


async def validate_user(username: str, password: str) -> tuple[str, str] | tuple[None, None]:

	user = None
	async with async_session() as s:
		result = await s.execute(select(Client).where(Client.username == username))
		user = result.scalars().first()

		# result.close()

	if not user:
		return None, None
	
	if not check_password(user.password, password):
		return str(user.uuid), None

	return str(user.uuid), str(user.uuid) + "." + apply_hash(str(user.uuid))