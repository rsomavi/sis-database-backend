-- ACTUALIZAR CAMPOS:
ALTER TABLE movies ADD COLUMN stock INT DEFAULT 10 NOT NULL CHECK (stock >= 0);
ALTER TABLE movies ADD COLUMN rating NUMERIC(3,2) DEFAULT 0;

ALTER TABLE clients ADD COLUMN country TEXT;
ALTER TABLE clients ADD COLUMN discount NUMERIC(5, 2) DEFAULT 0 CHECK (discount >= 0 AND discount <= 100);


ALTER TABLE orders ADD COLUMN total NUMERIC(9, 2) CHECK (total >= 0);
ALTER TABLE orders ADD COLUMN discount NUMERIC(5, 2) DEFAULT 0 CHECK (discount >= 0 AND discount <= 100);
ALTER TABLE orders ADD COLUMN final_price NUMERIC(9, 2) CHECK (final_price >= 0);


-- TRIGGERS PARA EL MOVIE STOCK:
CREATE OR REPLACE FUNCTION after_handle_movie_stock()
RETURNS TRIGGER AS $$
BEGIN
	-- es un insert o delete de table carts

	IF TG_OP = 'INSERT' THEN

		-- no deberia de dar error de num negativo
		UPDATE movies SET stock = stock - 1 WHERE id = NEW.movie_id;
		-- RETURN NEW;

	ELSIF TG_OP = 'DELETE' THEN

		UPDATE movies SET stock = stock + 1 WHERE id = OLD.movie_id;
		-- RETURN OLD;
	END IF;

	RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER tr_after_handle_movie_stock
AFTER INSERT OR DELETE ON carts
FOR EACH ROW
EXECUTE FUNCTION after_handle_movie_stock();

CREATE OR REPLACE FUNCTION before_handle_movie_stock()
RETURNS TRIGGER AS $$
BEGIN
	-- solo es de insert
	IF (SELECT stock FROM movies m WHERE m.id = NEW.movie_id) = 0 THEN
		RAISE EXCEPTION 'no hay stock suficiente | 409';
	END IF;
	
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER tr_before_handle_movie_stock
BEFORE INSERT ON carts
FOR EACH ROW
EXECUTE FUNCTION before_handle_movie_stock();

-- FUNCION PARA EL CARRITO Y LOS ORDERS
CREATE OR REPLACE FUNCTION add_to_cart(client_uuid UUID, mov_id INT)
RETURNS void AS $$
DECLARE
	cl_id INT;
	or_id INT;
BEGIN
	cl_id := NULL;
	or_id := NULL;

	SELECT o.id, c.id INTO or_id, cl_id
	FROM orders o 
	LEFT JOIN clients c ON c.id = o.client_id
	WHERE c.uuid = client_uuid AND o.state = 'open';

	-- si no existe carrito abierto para el usuario 'client_id'
	IF or_id IS NULL THEN
		-- entonces se crea
		INSERT INTO orders (client_id) 
		SELECT u.id FROM clients u WHERE u.uuid = client_uuid -- porque como ha fallado consul anterior no se tiene el client_id
		RETURNING id, client_id INTO or_id, cl_id;
	END IF;

	-- devuelve todas las peliculas compradas del usuario al que queremos añadir y comprueba si ya esta ahi
	-- evita que haya nulls (habia otras formas tambien) y asi siempre se computa bien el IN
	IF EXISTS (
		SELECT ca.movie_id
		FROM carts ca
		JOIN orders o ON o.id = ca.order_id
		WHERE o.client_id = cl_id
		AND ca.movie_id = mov_id
		LIMIT 1)
	THEN
		RAISE EXCEPTION 'pelicula ya comprada o agregada al carrito | 409';
	END IF;

	-- se hace lo del select por si la pelicula no existe pero se podria dejar sin nada y que de integrityerror normal
	INSERT INTO carts (order_id, movie_id)
		SELECT or_id, m.id 
		FROM movies m 
		WHERE m.id = mov_id 
		LIMIT 1;

	-- esto significa que no ha introducido ninguna row ya que el movie_id no es valido vvv
	IF NOT FOUND THEN
		RAISE EXCEPTION 'pelicula no encontrada | 404';
	END IF; 
END;
$$ LANGUAGE plpgsql;


-- CREATE OR REPLACE TRIGGER tr_handle_cart_addition
-- BEFORE INSERT ON carts
-- FOR EACH ROW
-- EXECUTE FUNCTION handle_cart_addition;

-- TRIGGER PARA ACTUALIZAR el precio CUANDO PAGA (antesde, before)
CREATE OR REPLACE FUNCTION handle_client_credit()
RETURNS TRIGGER AS $$
DECLARE
	total NUMERIC(9, 2);
	to_pay NUMERIC(9, 2);
	bal NUMERIC(9, 2);
	dis NUMERIC(5, 2);
BEGIN
	total := NULL;
	to_pay := NULL;
	bal := NULL;
	dis := NULL;

	SELECT cl.balance, cl.discount, sum(m.price) INTO bal, dis, to_pay
	FROM carts ca 
	INNER JOIN orders o ON ca.order_id = o.id
	INNER JOIN clients cl ON o.client_id = cl.id
	LEFT JOIN movies m ON ca.movie_id = m.id
	WHERE o.client_id = NEW.client_id AND o.state = 'open'
	GROUP BY cl.balance, cl.discount;

	IF to_pay IS NULL OR bal IS NULL THEN
		-- aqui entra si el carrito esta vacio, tiene orden abierta pero ningun producto
		RAISE EXCEPTION 'el cliente no tiene ningun carrito abierto por el momento | 404';
	END IF;

	total := to_pay;
	to_pay := ROUND(to_pay * (100 - dis) / 100, 2);

	IF to_pay > bal THEN
		RAISE EXCEPTION 'sin el balance suficiente, cliente: %, a pagar: % | 402', bal, to_pay;
	END IF;

	UPDATE clients
	SET balance = bal - to_pay
	WHERE id = NEW.client_id;

	NEW.discount := dis;
	NEW.total := total;
	NEW.final_price := to_pay;
	NEW.bought_at := CURRENT_DATE;

	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER tr_handle_client_credit
BEFORE UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION handle_client_credit();

-- TODO LO DE RECALCULAR EL AVERAGE DE LAS PELICULAS:

CREATE OR REPLACE FUNCTION compute_movie_rating(mov_id INT)
RETURNS NUMERIC(3, 2) AS $$
DECLARE
	rating NUMERIC(3, 2);
BEGIN
	SELECT ROUND(COALESCE(AVG(v.rating), 0), 2) INTO rating
	FROM movies m
	LEFT JOIN votes v ON v.movie_id = m.id
	WHERE m.id = mov_id;

	RETURN rating;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_movie_rating()
RETURNS TRIGGER AS $$
DECLARE
	mov_id INT;
BEGIN
	IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
		mov_id := NEW.movie_id;
	-- ELSIF TG_OP IS 'DELETE' THEN
	ELSE
		mov_id := OLD.movie_id;
	END IF;

	UPDATE movies m
	SET rating = compute_movie_rating(mov_id)
	WHERE m.id = mov_id;

	RETURN NULL; -- es after trigger no se devuelve nada
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER tr_update_movie_rating
AFTER INSERT OR DELETE OR UPDATE ON votes
FOR EACH ROW
EXECUTE FUNCTION update_movie_rating();