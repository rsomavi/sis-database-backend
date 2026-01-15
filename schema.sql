CREATE TABLE IF NOT EXISTS clients (
    id              SERIAL PRIMARY KEY,
    uuid			UUID NOT NULL DEFAULT gen_random_uuid(),

    username        VARCHAR(50)  NOT NULL UNIQUE,
    password		VARCHAR(100) NOT NULL,
    role            VARCHAR(30)  NOT NULL DEFAULT 'user',
	balance			NUMERIC(9, 2) NOT NULL CHECK (balance >= 0) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS movies (
    id              SERIAL PRIMARY KEY,
    
	title           VARCHAR(80) NOT NULL,
	description		TEXT DEFAULT 'sin descripción',
    release_date	DATE NOT NULL DEFAULT CURRENT_DATE,
    genre           VARCHAR(80),
    price           NUMERIC(5, 2) NOT NULL CHECK (price >= 0)
);

CREATE TABLE IF NOT EXISTS votes (
	client_id	INT NOT NULL,
	movie_id	INT NOT NULL,

	rating		NUMERIC(2,1) NOT NULL CHECK (rating >= 0 and rating <= 5),
	comment		TEXT,

	posted_at	TIMESTAMP NOT NULL DEFAULT NOW(),

	PRIMARY KEY (client_id, movie_id),
	FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
	FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS orders (
	id 			SERIAL PRIMARY KEY, -- order_id
	client_id	INT NOT NULL,
	
	-- estados:
	-- open, "ongoing" o que esta en el carrito
	-- closed, ya se ha realizado el pedido, se ha pagado
    state       VARCHAR(30)  NOT NULL DEFAULT 'open',
	bought_at	DATE,

	FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS carts ( -- order_items
	order_id	INT NOT NULL,
	movie_id	INT NOT NULL,

	PRIMARY KEY (order_id, movie_id),
	FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
	FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS actors (
	id              SERIAL PRIMARY KEY,

    name            VARCHAR(160) NOT NULL
);

CREATE TABLE IF NOT EXISTS movie_cast (
	movie_id		INT NOT NULL,
	actor_id		INT NOT NULL,

	PRIMARY KEY (movie_id, actor_id),
	FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
	FOREIGN KEY (actor_id) REFERENCES actors(id) ON DELETE CASCADE
);


CREATE INDEX IF NOT EXISTS idx_client_uuid ON clients (uuid);
-- CREATE INDEX IF NOT EXISTS ix_people_name ON people (name);

