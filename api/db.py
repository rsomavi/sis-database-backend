from sqlalchemy import text 
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import IntegrityError, DBAPIError

import os
from datetime import date

DB_URL = f'postgresql+asyncpg://{os.environ["DB_USER"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}'
engine = create_async_engine(DB_URL, echo=True)

async def user_exists(user_uuid: str) -> bool:
	async with engine.connect() as c:
		response = await c.execute(text("SELECT id FROM clients WHERE uuid = :user_uuid LIMIT 1;"), {"user_uuid": user_uuid})
		return response.first() != None

async def fetch_movies(params: dict[str, any] = {}) -> list[dict[str, str] | None]:
	query = "SELECT m.id, m.title, m.description, m.release_date, m.genre, m.price, m.rating, m.stock FROM movies m"

	if "actor" in params:
		query = f"{query} LEFT JOIN movie_cast mc ON mc.movie_id = m.id LEFT JOIN actors a ON a.id = mc.actor_id"

	len_params = len(params) - (1 if "limit" in params else 0)

	if len_params:
		query = f"{query} WHERE"

		if "title" in params:
			query = f"{query} LOWER(m.title) LIKE '%' || LOWER(:title) || '%' AND"
		
		if "year" in params:
			query = f"{query} EXTRACT(year FROM m.release_date) = :year AND"
			params.pop("date", None)
		elif "date" in params:
			query = f"{query} m.release_date = :date AND"
		
		if "genre" in params:
			query = f"{query} LOWER(m.genre) = LOWER(:genre) AND"

		if "max_price" in params:
			query = f"{query} m.price <= :max_price AND"

		if "actor" in params:
			query = f"{query} LOWER(a.name) LIKE '%' || LOWER(:actor) || '%' AND"

		query = query[:-4] # quita el ultimo " AND"

	query = f"{query} GROUP BY m.id, m.title, m.description, m.release_date, m.genre, m.price ORDER BY rating DESC"

	if "limit" in params:
		query = f"{query} LIMIT :limit"

	query += ";" 

	movies = []
	async with engine.connect() as c:
		# print("params:")
		# print(params)
		# print("query:")
		# print(query)

		result = await c.execute(text(query), params)

		movies = result.mappings().all()
		movies = [{k if k != "id" else "movieid": v for k, v in m.items()} | {"year": m["release_date"].year if m["release_date"] else None} for m in movies]

		# print(movies)

	return movies

async def fetch_movie_id(movie_id: int) -> dict[str, any] | None:
	async with engine.connect() as c:
		result = await c.execute(text("SELECT m.id, m.title, m.description, m.release_date, m.genre, m.price, m.rating, m.stock FROM movies m WHERE id = :movie_id;"), {"movie_id": movie_id})

		m = result.mappings().first()

		if not m:
			return None

		# se podria hacer en la consulta de arriba pero bueno
		actors = []
		if m["id"]:
			result = await c.execute(text("SELECT a.name FROM actors a LEFT JOIN movie_cast mc ON a.id = mc.actor_id WHERE mc.movie_id = :movie_id"), {"movie_id": m["id"]})
			actors = [a[0] for a in result.all()]

		return {k if k != "id" else "movieid": v for k, v in m.items()} | {"year": m["release_date"].year if m["release_date"] else None, "actors": actors}

async def handle_cart_addition(user_uuid: str, movie_id: int):
	# se comprueba si el usuario tiene una orden abierta (carrito activo)
	async with engine.connect() as c:
		try:
			# gestiona la creacion del cart si no esta creado y comprueba que el usuario no tiene ya la pelicula. los erroes encontrados se raisean con el status code para la api
			await c.execute(text("SELECT add_to_cart(:user_uuid, :movie_id);"), {"user_uuid": user_uuid, "movie_id": movie_id})
			await c.commit()
			return {"message": "pelicula guardada en el carrito correctamente"}, 200
		
		except DBAPIError as e:
			# forma bastante fea de sacar el error pero es lo que hay
			msg, st = e.orig.args[0].split('>: ')[1].split(" | ")

			await c.rollback()
			return {"error": msg}, int(st)

async def handle_cart_removal(user_uuid: str, movie_id: int) -> bool:
	async with engine.connect() as c:
		result = await c.execute(text("DELETE FROM carts ca USING orders o, clients cl WHERE ca.order_id = o.id AND cl.id = o.client_id AND cl.uuid = :user_uuid AND ca.movie_id = :movie_id AND o.state = 'open';"), {"user_uuid": user_uuid, "movie_id": movie_id})
		await c.commit()

		return result.rowcount != 0

async def fetch_cart(user_uuid:str) -> list[dict[str, str] | None]:
	movies = []
	async with engine.connect() as c:
		# VVV MUCHA MEJOR RESPUESTA PERO COMO EL CLIENTE.PY ESPERA SOLO EL ARRAY DE PELICULAS NO SIRVE VVV
		# result = await c.execute(text("""
		# 	SELECT ARRAY_AGG(json_build_object('movieid', m.id, 'title', m.title, 'rating', m.rating, 'price', m.price)) as movies,
		# 			cl.balance,
		# 			cl.discount,
		# 			SUM(m.price) as total,
		# 			ROUND(SUM(m.price) * (100 - cl.discount) / 100, 2) as discounted_price
		# 	FROM carts ca 
		# 	INNER JOIN orders o ON ca.order_id = o.id
		# 	INNER JOIN clients cl ON o.client_id = cl.id
		# 	LEFT JOIN movies m ON ca.movie_id = m.id
		# 	WHERE cl.uuid = :user_uuid AND o.state = 'open'
		# 	GROUP BY cl.balance, cl.discount;
		# 						"""), {"user_uuid": user_uuid})
		# movies = dict(result.mappings().first() or {})
		# if movies:
		# 	movies["movies"] = movies.get("movies", [])
		# return movies
		# movies = [{k if k != "id" else "movieid": v for k, v in m.items()} for m in movies]
		
		
		# solo devolvemos informacion relevante sobre las peliculas (no stock, no rating)
		result = await c.execute(text("""
			SELECT m.id as movieid, m.title, m.description, m.release_date, m.genre, m.price FROM carts ca 
			INNER JOIN orders o ON ca.order_id = o.id
			INNER JOIN clients cl ON o.client_id = cl.id
			LEFT JOIN movies m ON ca.movie_id = m.id
			WHERE cl.uuid = :user_uuid AND o.state = 'open';
								"""), {"user_uuid": user_uuid})
		
		movies = result.mappings().all()
		movies = [dict(m) for m in movies]

	return movies

async def close_cart(user_uuid: str) -> tuple[dict[str, str], int]:
	async with engine.connect() as c:
		try:
			# con solo querer cerrar el carrito los triggers se ocupan de comprobar si tiene saldo suficiente, y lo restan si se puede comprar
			# print("cerrar pedido...")
			result = await c.execute(text("""
			UPDATE orders o SET state = 'closed'
			FROM clients c 
			WHERE o.state = 'open' AND c.uuid = :user_uuid AND c.id = o.client_id
			RETURNING o.id;"""), {"user_uuid": user_uuid})
			# print("pedido cerrado.")

			# print("sleep en db...")
			# result = await c.execute(text("SELECT pg_sleep(20);"))
			# print("sleep completado")

			# print("commiteando...")
			await c.commit()

			result = result.mappings().first()
			if result:
				return {"orderid": result.get("id")}, 200
			else:
				# no hace falta hacer rollback, no hay cambios
				return {"error": "no tienes ningun carrito abierto por el momento"}, 404

		except DBAPIError as e:
			msg, st = e.orig.args[0].split('>: ')[1].split(" | ")

			await c.rollback()
			return {"error": msg}, int(st)

	
async def update_balance(user_uuid: str, balance: float | int) -> tuple[dict[str, str], int]:
	new_balance = 0
	async with engine.connect() as c:
		result = await c.execute(text("UPDATE clients SET balance = balance + :balance WHERE uuid = :user_uuid RETURNING balance;"), {"user_uuid": user_uuid, "balance": balance})

		# no deberia de ser nulo		
		new_balance = result.mappings().first()
		new_balance = new_balance["balance"] if new_balance else 0

		await c.commit()

	return {"new_credit": new_balance}, 200

async def fetch_balance(user_uuid: str):
	async with engine.connect() as c:
		result = await c.execute(text("SELECT balance FROM clients WHERE uuid = :user_uuid;"), {"user_uuid": user_uuid})

		# no deberia de ser nulo		
		balance = result.mappings().first()
		balance = balance["balance"] if balance else 0.00
		
		return {"credit": balance}, 200

async def fetch_order(user_uuid: str, order_id: int):
	async with engine.connect() as c:

		result = await c.execute(text("""
								SELECT cl.uuid, o.bought_at as date, o.total, o.final_price as discounted_price, o.discount,
								ARRAY_AGG(json_build_object('movieid', m.id, 'title', m.title, 'description', m.description, 'release_date', m.release_date, 'genre', m.genre, 'price', m.price)) as movies   
								FROM orders o 
								INNER JOIN carts c ON c.order_id = o.id 
								LEFT JOIN movies m ON m.id = c.movie_id 
								LEFT JOIN clients cl ON cl.id = o.client_id 
								WHERE o.state = 'closed' AND o.id = :order_id 
								GROUP BY cl.uuid, o.bought_at, o.total, o.final_price, o.discount
								LIMIT 1;"""), {"order_id": order_id})

		info = result.mappings().first()
		if not info:
			return {"error": "no se ha encontrado orden con esa id"}, 404
		

		if str(info["uuid"]) != user_uuid:
			return {"error": "no se puede ver orden agena"}, 403
		
		info = dict(info)
		info.pop("uuid")

		return info, 200


async def put_movie_vote(user_uuid: str, movie_id: int, rating: float, comment: str | None) -> tuple[dict[str, str], int]:
	st = 200
	
	async with engine.connect() as c:

		result = await c.execute(text("UPDATE votes SET rating = :rating, comment = :comment, posted_at = NOW() FROM clients cl WHERE cl.id = client_id AND movie_id = :movie_id AND cl.uuid = :user_uuid;"), {"user_uuid": user_uuid, "movie_id": movie_id, "rating": rating, "comment": comment})

		if result.rowcount == 0:
			# hay que crearlo, no existe

			try:
				await c.execute(text("INSERT INTO votes (client_id, movie_id, rating, comment) SELECT cl.id, :movie_id, :rating, :comment FROM clients cl WHERE cl.uuid = :user_uuid;"), {"user_uuid": user_uuid, "movie_id": movie_id, "rating": rating, "comment": comment})
				st = 201
				await c.commit()

			except IntegrityError:
				await c.rollback()
				return {"error": "pelicula no encontrada"}, 404
		else:
			await c.commit()

		return {"message": "voto emitido correctamente"}, st
	
async def delete_movie_vote(user_uuid, movie_id):
	async with engine.connect() as c:
		result = await c.execute(text("DELETE FROM votes v USING clients c WHERE c.id = v.client_id AND v.movie_id = :movie_id AND c.uuid = :user_uuid;"), {"user_uuid": user_uuid, "movie_id": movie_id})
		await c.commit()

		if result.rowcount == 0:
			return {"error": "no se ha encontrado voto o pelicula"}, 404
	
		return {"message": "voto borrado correctamente"}, 200

async def fetch_client_votes(user_uuid: str) -> tuple[dict[str, str], int]:
	async with engine.connect() as c:
		result = await c.execute(text("SELECT id FROM clients WHERE uuid = :user_uuid LIMIT 1;"), {"user_uuid": user_uuid})
		
		user = result.first()
		if not user:
			return {"error": "usuario no encontrado"}, 404

		result = await c.execute(text("SELECT m.id as movieid, m.title, v.rating, v.comment, v.posted_at FROM votes v INNER JOIN movies m ON m.id = v.movie_id WHERE v.client_id = :user_id;"), {"user_id": user[0]})

		votes = result.mappings().all()
		return {"votes": [dict(v) for v in votes]}, 200
	
async def fetch_client_info(user_uuid: str) -> tuple[dict[str, str], int]:
	async with engine.connect() as c:

		info = {}
		result = await c.execute(text("""
SELECT 
	   cl.id,
	   cl.uuid,
	   cl.username,
	   cl.role,
	   cl.balance,
	   cl.discount,
	   cl.country,
	   COALESCE(
      JSON_AGG(json_build_object('movieid', ca.movie_id, 'title', m.title, 'description', m.description, 'rating', m.rating))
     FILTER (WHERE ca.movie_id IS NOT NULL AND o.state = 'closed'),
     '[]'
      ) AS movies_bought
FROM clients cl
LEFT JOIN orders o ON o.client_id = cl.id
LEFT JOIN carts ca ON ca.order_id = o.id
LEFT JOIN movies m ON m.id = ca.movie_id
WHERE cl.uuid = :user_uuid
GROUP BY 
	   cl.id,
	   cl.uuid,
	   cl.username,
	   cl.role,
	   cl.balance,
	   cl.discount,
	   cl.country
LIMIT 1;
"""), {"user_uuid": user_uuid})
		
		info = dict(result.mappings().first())
		# info["movies_bought"] = dict(info["movies_bought"])
		
		# movies_bought deberia ser siempre un array aunque sea vacio, nunca null, gracias al coalesce; pero por si acaso
		info["movies_bought"] = [dict(f) for f in info.get("movies_bought", []) if f]

		result = await c.execute(text("""
SELECT v.movie_id as movieid, m.title, v.rating, v.comment, v.posted_at
FROM votes v
LEFT JOIN movies m ON m.id = v.movie_id
WHERE v.client_id = :id;
"""), {"id": info["id"]})
		
		info["comments"] = [dict(m) for m in result.mappings().all()]
		info.pop("id", None)

		return info, 200

async def is_admin(user_uuid: str) -> bool:
	async with engine.connect() as c:
		result = await c.execute(text("SELECT role = 'admin' FROM clients WHERE uuid = :user_uuid LIMIT 1;"), {"user_uuid": user_uuid})

		return result.first()[0] # deberia de devolver al menos una row

async def fetch_clientes_sin_pedidos() -> tuple[list[dict[str, str]], int]:
	async with engine.connect() as c:
		result = await c.execute(text("""SELECT c.id, c.balance, c.country, c.discount, c.role, c.username, c.uuid FROM clients c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.client_id = c.id AND o.state = 'closed');"""))

		result = result.mappings().all()
		return [dict(r) for r in result], 200

async def fetch_stats(year: str | int, country: str):

	async with engine.connect() as c:
# 		result = c.execute(text(f"""
# SELECT  o.id as orderid, o.bought_at, o.total, o.discount, o.final_price,
# 		cl.id as client_id, cl.uuid, cl.username, cl.balance, cl.country, cl.discount, 
# 		ARRAY_AGG(ROW(m.id as movieid, m.title, m.description, m.release_date, m.genre, m.price)) as products 
# FROM orders o
# LEFT JOIN carts ca ON ca.order_id = o.id
# LEFT JOIN clients cl ON o.client_id = cl.id
# LEFT JOIN movies m ON m.id = ca.movie_id
# WHERE {'EXTRACT(YEAR FROM o.bought_at) = :year' if year != 'all' else 'o.bought_at IS NOT NULL'} 
# 	AND LOWER(cl.country) LIKE {'LOWER(:country)' if country != 'all' else "'%'"}
# GROUP BY o.id, cl.id;
# """
# ), {"year": year, "country": country})
		
		result = await c.execute(text(f"""
SELECT cl.id AS client_id, cl.uuid, cl.username, cl.balance, cl.country, cl.discount, SUM(o.final_price) AS total_gastado,
       ARRAY_AGG(json_build_object('orderid', o.id, 'bought_at', o.bought_at, 'total', o.total, 'discount', o.discount, 'final_price', o.final_price)) AS orders
FROM clients cl
LEFT JOIN orders o ON cl.id = o.client_id 
WHERE {"o.bought_at >= :year AND o.bought_at <  :year2" if year != 'all' else 'o.bought_at IS NOT NULL'}
{'AND LOWER(cl.country) LIKE LOWER(:country)' if country != 'all' else ""}
GROUP BY cl.id,
         cl.uuid,
         cl.username,
         cl.balance,
         cl.country,
         cl.discount;"""
), {"year": date(year if year != "all" else 2000, 1, 1), "year2":  date(year + 1 if year != "all" else 2000, 1, 1), "country": country})

		result = result.mappings().all()
		# result["orders"] = [{"orderid": o["orderid"], "bought_at": o["bought_at"], "total": o["total"], "discount": o["discount"], "final_price": o["final_price"], "products": dict(o["products"])} for o in result["orders"]]

		return [dict(r) for r in result], 200

async def delete_clients_from(country: str) -> tuple[dict[str, str], int]:
	async with engine.connect() as c:

		if country.lower() == "null":
			where = "c.country IS NULL"
		else:
			where = "LOWER(c.country) = LOWER(:country)"

		# se tienen que borrar primero votes y orders antes que clients
		print("borrando todo de votes...")
		await c.execute(text(f"DELETE FROM votes v USING clients c WHERE c.id = v.client_id AND {where};"), {"country": country})
		
		print("borrando todo de carts...")
		await c.execute(text(f"DELETE FROM carts ca USING orders o, clients c WHERE ca.order_id = o.id AND o.client_id = c.id AND {where};"), {"country": country})

		print("borrando todo de orders...")
		await c.execute(text(f"DELETE FROM orders o USING clients c WHERE c.id = o.client_id AND {where};"), {"country": country})
		
		print("borrando todo de clients...")
		result = await c.execute(text(f"DELETE FROM clients c WHERE {where}"), {"country": country})

		print("no hay fallo, haciendo commit...")
		await c.commit()

		return {"message": f"se han borrado {result.rowcount} clientes"}, 200
	
async def delete_clients_error_from(country: str) -> tuple[dict[str, str], int]:
	async with engine.connect() as c:

		if country.lower() == "null":
			where = "c.country IS NULL"
		else:
			where = "LOWER(c.country) = LOWER(:country)"

		# dara error porque no puede borrar ya que hay otras tablas que dependen de esta
		result = None
		try:
			print("borrando clients...")
			result = await c.execute(text(f"DELETE FROM clients c WHERE {where}"), {"country": country})
			
			print("borrando votes...")
			await c.execute(text(f"DELETE FROM votes v USING clients c WHERE c.id = v.client_id AND {where};"), {"country": country})

			print("borrando orders...")
			await c.execute(text(f"DELETE FROM orders o USING clients c WHERE c.id = o.client_id AND {where};"), {"country": country})

			print("borrando carts...")
			await c.execute(text(f"DELETE FROM carts ca USING orders o, clients c WHERE ca.order_id = o.id AND o.client_id = c.id AND {where};"), {"country": country})

			print("no hay fallo, haciendo commit...")
			await c.commit()
		except IntegrityError:

			print("error, haciendo rollback...")
			await c.rollback()
			return {"error": "no se ha podido borrar. comportamiento esperado"}, 400

		# nunca pasara de aqui (a no ser que no haya usuarios de ese pais); 0 clientes borrados

		return {"message": f"se han borrado {result.rowcount} clientes"}, 200

async def delete_clients_intermedio_from(country: str) -> tuple[dict[str, str], int]:
	async with engine.connect() as c:
		print("actualizando balance...")
		await c.execute(text("UPDATE clients SET balance = balance + 10;"))
		print("guardando balance, haciendo commit...")
		await c.commit()

		if country.lower() == "null":
			where = "c.country IS NULL"
		else:
			where = "LOWER(c.country) = LOWER(:country)"

		result = None
		try:
			print("borrando clients...")
			result = await c.execute(text(f"DELETE FROM clients c WHERE {where}"), {"country": country})
			
			print("borrando votes...")
			await c.execute(text(f"DELETE FROM votes v USING clients c WHERE c.id = v.client_id AND {where};"), {"country": country})

			print("borrando orders...")
			await c.execute(text(f"DELETE FROM orders o USING clients c WHERE c.id = o.client_id AND {where};"), {"country": country})

			print("borrando carts...")
			await c.execute(text(f"DELETE FROM carts ca USING orders o, clients c WHERE ca.order_id = o.id AND o.client_id = c.id AND {where};"), {"country": country})

			print("no hay fallo, haciendo commit...")
			await c.commit()
		except IntegrityError:

			print("error, haciendo rollback...")
			await c.rollback()
			return {"error": "no se ha podido borrar. comportamiento esperado"}, 400

		# nunca pasara de aqui (a no ser que no haya usuarios de ese pais); 0 clientes borrados

		return {"message": f"se han borrado {result.rowcount} clientes"}, 200


async def remove_on_cascade():
	async with engine.connect() as c:
		await c.execute(text("ALTER TABLE votes DROP CONSTRAINT votes_client_id_fkey;"))
		await c.execute(text("ALTER TABLE orders DROP CONSTRAINT orders_client_id_fkey;"))
		await c.execute(text("ALTER TABLE carts DROP CONSTRAINT carts_order_id_fkey;"))
		await c.execute(text("ALTER TABLE votes ADD CONSTRAINT votes_client_id_fkey FOREIGN KEY (client_id) REFERENCES clients(id);"))
		await c.execute(text("ALTER TABLE orders ADD CONSTRAINT orders_client_id_fkey FOREIGN KEY (client_id) REFERENCES clients(id);"))
		await c.execute(text("ALTER TABLE carts ADD CONSTRAINT carts_order_id_fkey FOREIGN KEY (order_id) REFERENCES orders(id);"))

		await c.commit()

async def add_on_cascade():
	async with engine.connect() as c:
		await c.execute(text("ALTER TABLE votes DROP CONSTRAINT votes_client_id_fkey;"))
		await c.execute(text("ALTER TABLE orders DROP CONSTRAINT orders_client_id_fkey;"))
		await c.execute(text("ALTER TABLE carts DROP CONSTRAINT carts_order_id_fkey;"))
		await c.execute(text("ALTER TABLE votes ADD CONSTRAINT votes_client_id_fkey FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE;"))
		await c.execute(text("ALTER TABLE orders ADD CONSTRAINT orders_client_id_fkey FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE;"))
		await c.execute(text("ALTER TABLE carts ADD CONSTRAINT carts_order_id_fkey FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE;"))

		await c.commit()

async def create_movie(params: dict[str, str]) -> tuple[dict[str, str], int]:
	defaults = {'description': 'sin descripción', 'stock': 10, 'release_date': date.today()}
	defaults.update(params)
	async with engine.connect() as c:
		try:
			result = await c.execute(text("INSERT INTO movies (title, description, release_date, genre, price, stock) VALUES (:title, :description, :release_date, :genre, :price, :stock) RETURNING *;"), defaults)
			await c.commit()

			return dict(result.mappings().first()), 201
		except:
			await c.rollback()

			return {"error": "faltan argumentos en el cuerpo o son del tipo incorrecto, {'title': ..., 'description': ..., 'release_date': ..., 'genre': ..., 'price': ..., 'stock': ...}"}, 400

async def replace_movie(params: dict[str, str]) -> tuple[dict[str, str], int]:
	defaults = {'description': 'sin descripción', 'stock': 10, 'release_date': date.today()}
	defaults.update(params)
	async with engine.connect() as c:
		try:
			result = await c.execute(text("UPDATE movies SET title = :title, description = :description, release_date = :release_date, genre = :genre, price = :price, stock = :stock WHERE id = :movieid RETURNING *;"), defaults)
			await c.commit()

			result = result.mappings().first()
			if not result:
				return {"error": "pelicula con id no encontrada"}, 404
			return dict(result), 200

		except:
			await c.rollback()

			return {"error": "faltan argumentos en el cuerpo o son del tipo incorrecto, {'title': ..., 'description': ..., 'release_date': ..., 'genre': ..., 'price': ..., 'stock': ..., 'movieid': ...}"}, 400

async def delete_movie(movie_id: int) -> tuple[dict[str, str], int]:
	async with engine.connect() as c:
		try:
			result = await c.execute(text("DELETE FROM movies WHERE id = :movieid;"), {"movieid": movie_id})
			await c.commit()

			if result.rowcount == 0:
				return {"error": "no se ha encontrado la pelicula, no se ha borrado nada"}, 404
			
			return {"message": "pelicula borrada correctamente"}, 200
		except:
			await c.rollback()
			return {"error": "faltan argumentos en el cuerpo o son del tipo inorrecto, {'movieid': id}"}, 400

async def client_discount(user_uuid:str, discount:int) -> tuple[dict[str, str], int]:
	async with engine.connect() as c:
		try:
			result = await c.execute(text("UPDATE clients SET discount = :discount WHERE uuid = :user_uuid;"), {"discount": discount, "user_uuid": user_uuid})
			await c.commit()

			if result.rowcount == 0:
				return {"error": "no se ha encontrado al usuario"}, 404
			
			return {"message": "discount actualizado correctamente"}, 200
		except:
			await c.rollback()
			return {"error": "falta valor para discount o es invalido"}, 400

async def force_deadlock(i):
	async with engine.connect() as c:
		if i:
			await c.execute(text("UPDATE clients SET balance = balance + 100 WHERE id = 1;"))
			await c.execute(text("SELECT pg_sleep(5);"))
			await c.execute(text("UPDATE clients SET balance = balance + 100 WHERE id = 2;"))
		else:
			await c.execute(text("UPDATE clients SET balance = balance + 100 WHERE id = 2;"))
			await c.execute(text("SELECT pg_sleep(5);"))
			await c.execute(text("UPDATE clients SET balance = balance + 100 WHERE id = 1;"))

		await c.commit()

