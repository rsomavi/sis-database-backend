-- si ya hay info borrar:
DELETE FROM votes;
DELETE FROM carts;
DELETE FROM orders;
DELETE FROM movie_cast;
DELETE FROM actors;
DELETE FROM movies;
DELETE FROM clients;

-- y reiniciar indices
ALTER SEQUENCE clients_id_seq RESTART WITH 1;
ALTER SEQUENCE movies_id_seq RESTART WITH 1;
ALTER SEQUENCE actors_id_seq RESTART WITH 1;
ALTER SEQUENCE orders_id_seq RESTART WITH 1;	

-- popular
INSERT INTO clients (username, password, role, balance, country) VALUES
('admin', '$argon2i$v=19$m=16,t=2,p=1$OTZHeExSNmQ0V2Y3WDJPMA$Gmgs3YDx9N3bhFOdndWoYQ', 'admin', 999, 'españa'),
('jose', '$argon2id$v=19$m=65536,t=3,p=4$qLcEl823GRaqHB53GAdGXQ$qY2yYy0yoNzy0UM/x49T78sb1xcd5c8GXJUGA0wjTVQ', 'user', 0, 'españa'),
('pedro', '$argon2id$v=19$m=65536,t=3,p=4$qLcEl823GRaqHB53GAdGXQ$qY2yYy0yoNzy0UM/x49T78sb1xcd5c8GXJUGA0wjTVQ', 'user', 6.7, 'españa'),
('pablo', '$argon2id$v=19$m=65536,t=3,p=4$qLcEl823GRaqHB53GAdGXQ$qY2yYy0yoNzy0UM/x49T78sb1xcd5c8GXJUGA0wjTVQ', 'user', 20.50, 'alemania'),
('ramon', '$argon2id$v=19$m=65536,t=3,p=4$qLcEl823GRaqHB53GAdGXQ$qY2yYy0yoNzy0UM/x49T78sb1xcd5c8GXJUGA0wjTVQ', 'user', 2.33, 'francia'),
('simon', '$argon2id$v=19$m=65536,t=3,p=4$qLcEl823GRaqHB53GAdGXQ$qY2yYy0yoNzy0UM/x49T78sb1xcd5c8GXJUGA0wjTVQ', 'user', 2, 'alemania'),
('adrian', '$argon2id$v=19$m=65536,t=3,p=4$qLcEl823GRaqHB53GAdGXQ$qY2yYy0yoNzy0UM/x49T78sb1xcd5c8GXJUGA0wjTVQ', 'user', 9.3, 'alemania'),
('mario', '$argon2id$v=19$m=65536,t=3,p=4$qLcEl823GRaqHB53GAdGXQ$qY2yYy0yoNzy0UM/x49T78sb1xcd5c8GXJUGA0wjTVQ', 'user', 10, 'españa');

INSERT INTO movies (title, release_date, genre, price, description) VALUES 
('Inception', '2010-07-16', 'Sci-Fi', 3.99, 'Un ladrón entra en los sueños para robar secretos corporativos.'),
('The Shawshank Redemption', '1994-09-23', 'Drama', 2.99, 'Un banquero encarcelado planea su escape y busca la redención.'),
('The Dark Knight', '2008-07-18', 'Action', 3.49, 'Batman enfrenta al Joker en una lucha por el alma de Gotham.'),
('Pulp Fiction', '1994-10-14', 'Crime', 2.79, 'Historias entrelazadas de crimen y redención en Los Ángeles.'),
('Forrest Gump', '1994-06-23', 'Drama', 2.99, 'La vida de un hombre sencillo que presencia grandes momentos históricos.'),
('The Matrix', '1999-03-31', 'Sci-Fi', 3.29, 'Un hacker descubre que el mundo es una simulación controlada por máquinas.'),
('Goodfellas', '1990-09-12', 'Crime', 2.89, 'La historia real de un gánster que asciende en la mafia neoyorquina.'),
('The Godfather', '1972-03-24', 'Crime', 3.19, 'El patriarca de una familia mafiosa lucha por mantener su poder.'),
('Fight Club', '1999-10-15', 'Drama', 3.09, 'Un hombre crea un club secreto de peleas para liberar su frustración.'),
('Interstellar', '2014-11-07', 'Sci-Fi', 3.79, 'Astronautas viajan a través de un agujero de gusano en busca de un nuevo hogar.'),
('The Prestige', '2006-10-20', 'Drama', 3.49, 'Dos magos rivales llevan su obsesión por superarse al extremo.'),
('Gladiator', '2000-05-05', 'Action', 3.29, 'Un general romano traicionado busca venganza en la arena.'),
('The Wolf of Wall Street', '2013-12-25', 'Biography', 3.99, 'Un corredor de bolsa se enriquece mediante el fraude y el exceso.'),
('Parasite', '2019-05-30', 'Thriller', 3.49, 'Una familia pobre se infiltra en la vida de una familia rica.'),
('Joker', '2019-10-04', 'Drama', 3.69, 'El origen oscuro de un hombre marginado que se convierte en villano.'),
('Avatar', '2009-12-18', 'Sci-Fi', 3.79, 'Un exmarine se une a una raza alienígena en un planeta exuberante.'),
('The Social Network', '2010-10-01', 'Drama', 2.99, 'La historia de la creación de Facebook y sus conflictos legales.'),
('Whiplash', '2014-10-10', 'Drama', 3.39, 'Un joven baterista busca la perfección bajo un exigente profesor.'),
('Mad Max: Fury Road', '2015-05-15', 'Action', 3.59, 'En un mundo postapocalíptico, una rebelde huye en busca de libertad.'),
('Dune', '2021-10-22', 'Sci-Fi', 4.19, 'Un joven noble lucha por su destino en un planeta desértico.'),
('Men in Black', '1997-07-02', 'Sci-Fi', 2.99, 'Agentes secretos protegen la Tierra de extraterrestres.'),
('Men in Black II', '2002-07-03', 'Sci-Fi', 3.19, 'Los agentes J y K vuelven para detener una amenaza alienígena.'),
('Men in Black 3', '2012-05-25', 'Sci-Fi', 3.49, 'J viaja en el tiempo para salvar a su compañero K.'),
('Men in Black: International', '2019-06-14', 'Sci-Fi', 3.69, 'Nuevos agentes enfrentan una conspiración dentro de la organización.'),
('The Matrix Reloaded', '2003-05-15', 'Sci-Fi', 3.29, 'Neo descubre nuevas verdades sobre el sistema que gobierna la Matrix.'),
('The Matrix Revolutions', '2003-11-05', 'Sci-Fi', 3.29, 'Neo libra la batalla final entre humanos y máquinas.'),
('The Matrix Resurrections', '2021-12-22', 'Sci-Fi', 3.79, 'Neo despierta de nuevo en un mundo que desafía su realidad.'),
('Gladiator I', '2000-12-22', 'Action', 2, 'Un guerrero lucha por su honor en el Imperio romano.'),
('Gladiator II', '2000-12-20', 'Action', 2, 'El legado del gladiador continúa con nuevas batallas.'),
('Gladiator III', '2001-12-22', 'Drama', 2, 'Un héroe cansado busca redención en la arena.'),
('Gladiator IV', '2001-12-22', 'Action', 2, 'El guerrero regresa para enfrentar a un enemigo implacable.'),
('Gladiator V', '2000-12-22', 'Drama', 2, 'Una nueva generación lucha por la libertad en Roma.'),
('Venom', '1999-10-10', 'Action', 4, 'Un periodista adquiere poderes tras unirse con un simbionte alienígena.');


INSERT INTO actors (name) VALUES 
('Leonardo DiCaprio'),
('Morgan Freeman'),
('Christian Bale'),
('John Travolta'),
('Tom Hanks'),
('Keanu Reeves'),
('Robert De Niro'),
('Marlon Brando'),
('Brad Pitt'),
('Matthew McConaughey'),
('Christopher Nolan'),
('Quentin Tarantino'),
('Frank Darabont'),
('Timothée Chalamet'),
('Margot Robbie'),
('Hugh Jackman'),
('Russell Crowe'),
('Jonah Hill'),
('Song Kang-ho'),
('Joaquin Phoenix'),
('Sam Worthington'),
('Jesse Eisenberg'),
('Miles Teller'),
('Charlize Theron'),
('Zendaya'),
('Rebecca Ferguson'),
('Jessica Chastain'),
('Edward Norton'),
('Natalie Portman'),
('Emma Stone'),
('Will Smith'),
('Tommy Lee Jones'),
('Josh Brolin'),
('Emma Thompson'),
('Tessa Thompson'),
('Chris Hemsworth'),
('Liam Neeson'),
('Rip Torn'),
('Rosario Dawson'),
('Linda Fiorentino'),
('Tom Hardy');


-- valores aleatorios
INSERT INTO movie_cast (movie_id, actor_id) VALUES
(1, 1),
(1, 2),
(1, 3),
(2, 4),
(2, 1),
(3, 7),
(4, 7),
(11, 1),  -- The Prestige: Hugh Jackman
(11, 3),  -- Christian Bale
(12, 2),  -- Gladiator: Russell Crowe
(13, 1),  -- Leonardo DiCaprio
(13, 3),  -- Jonah Hill
(14, 4),  -- Parasite: Song Kang-ho
(15, 5),  -- Joker: Joaquin Phoenix
(16, 6),  -- Avatar: Sam Worthington
(17, 7),  -- The Social Network: Jesse Eisenberg
(18, 8),  -- Whiplash: Miles Teller
(19, 9),  -- Mad Max: Charlize Theron
(20, 10), -- Dune: Zendaya
(20, 11), -- Dune: Rebecca Ferguson
-- Men in Black (1997)
(21, 31),  -- Will Smith
(21, 32),  -- Tommy Lee Jones
(21, 40),  -- Linda Fiorentino
(21, 38),  -- Rip Torn

-- Men in Black II (2002)
(22, 31),  -- Will Smith
(22, 32),  -- Tommy Lee Jones
(22, 38),  -- Rip Torn
(22, 39),  -- Rosario Dawson

-- Men in Black 3 (2012)
(23, 31),  -- Will Smith
(23, 32),  -- Tommy Lee Jones
(23, 33),  -- Josh Brolin (joven K)
(23, 38),  -- Rip Torn
(23, 34),  -- Emma Thompson

-- Men in Black: International (2019)
(24, 35),  -- Tessa Thompson
(24, 36),  -- Chris Hemsworth
(24, 37),  -- Liam Neeson
(24, 34),  -- Emma Thompson (repite su papel)
(1, 41),  -- Inception: Tom Hardy
(6, 6),   -- The Matrix
(7, 6),   -- Matrix Reloaded
(8, 6),   -- Matrix Revolutions
(9, 6),   -- Matrix Resurrections
(9, 41),  -- Tom Hardy cameo (ficticio)
(22, 41), -- Mad Max: Fury Road - Tom Hardy
(23, 41), --  Tom Hardy
(23, 15), --  Michelle Williams
(33, 41), -- Venom - Tom Hardy
(33, 15); -- Venom - Michelle Williams

INSERT INTO votes (client_id, movie_id, rating, comment) VALUES 
(2, 1, 5, 'Una obra maestra de Nolan. La trama es increíble!'),
(2, 3, 5, 'Heath Ledger fue increíble como el Joker.'),
(3, 5, 4.5, 'Tom Hanks estuvo brillante.'),
(4, 6, 5, 'Revolucionó el cine de ciencia ficción.'),
(5, 8, 0.2, 'La peor película de la historia, sin duda.'),
(1, 4, 3, 'Interesante pero un poco confusa.'),
(2, 7, 4, 'Buen retrato de la mafia italiana.'),
(2, 11, 4.8, 'Nolan nunca decepciona, increíble historia de rivalidad.'),
(3, 12, 4.9, 'Épica, emocionante y con una banda sonora brutal.'),
(4, 13, 4.2, 'Una locura de película, DiCaprio desatado.'),
(5, 14, 5, 'La mejor película coreana que he visto.'),
(6, 15, 4.7, 'El Joker de Phoenix es perturbador y genial.'),
(7, 16, 3.8, 'Visualmente impactante, pero la historia flojea un poco.'),
(8, 17, 4.3, 'Genial retrato del nacimiento de Facebook.'),
(2, 18, 4.9, 'La tensión entre profesor y alumno es brutal.'),
(3, 19, 4.5, 'Acción sin descanso, Charlize la rompe.'),
(4, 20, 4.6, 'Visualmente espectacular, muy bien lograda.'),
(5, 1, 4.9, 'Inception sigue siendo una de mis favoritas.'),
(6, 2, 3.5, 'Buena historia, pero un poco lenta para mi gusto.'),
(2, 21, 4.5, 'Divertidísima, una mezcla perfecta entre acción y humor.'),
(3, 22, 4.2, 'No tan buena como la primera, pero Will Smith la mantiene viva.'),
(4, 23, 4.8, 'Excelente cierre de trilogía. La historia con el tiempo es genial.'),
(5, 24, 3.9, 'Tessa y Chris tienen buena química, aunque la historia flojea.'),
(6, 21, 4.6, 'Un clásico de mi infancia, puro entretenimiento.'),
(7, 23, 4.7, 'Josh Brolin haciendo de Tommy Lee Jones joven es brutal.'),
(8, 24, 3.5, 'Visualmente buena, pero sin la chispa de las originales.');


INSERT INTO orders (client_id, state, bought_at, total, final_price, discount) VALUES
(2, 'closed', '2024-12-01', 1, 1, 0),
(3, 'closed', '2024-12-02', 12, 12, 0),
(4, 'closed', '2024-12-05', 1, 1, 0),
(5, 'closed', '2024-12-10', 1, 1, 0),
(6, 'open', NULL, NULL, NULL, NULL),
(7, 'closed', '2024-12-15', 1, 1, 0),
(8, 'closed', '2024-12-20', 10, 10, 0),
(2, 'closed', '2025-01-10', 10, 5, 50),
(3, 'closed', '2025-01-12', 1, 1, 0),
(4, 'open', NULL, NULL, NULL, NULL),
(5, 'closed', '2025-01-20', 15, 15, 0);

INSERT INTO carts (order_id, movie_id) VALUES
(1, 1),
(1, 3),
(2, 5),
(2, 6),
(3, 13),
(3, 11),
(4, 14),
(4, 15),
(5, 16),
(5, 20),
(6, 18),
(7, 19),
(7, 10),
(8, 21),
(8, 22),
(9, 23),
(10, 24);
