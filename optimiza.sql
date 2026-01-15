CREATE INDEX idx_clients_country_lower ON clients (LOWER(country));
CREATE INDEX idx_orders_client_id ON orders (client_id);
CREATE INDEX idx_orders_bought_at ON orders (bought_at);
