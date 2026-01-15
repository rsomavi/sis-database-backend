# Database Backend System

Academic backend project focused on advanced relational database concepts and
containerized deployment using Docker.

## Overview
This project implements a database-driven backend system with support for
transactions, concurrency control, and automated logic through SQL triggers.
The system is deployed using Docker Compose and is designed to demonstrate
advanced database usage beyond basic CRUD operations.

## Technologies
- Python
- PostgreSQL
- SQL (triggers, transactions, concurrency control)
- Docker & Docker Compose

## Project Structure
- `api/` – Backend API services
- `user/` – User-related services
- `schema.sql` – Database schema definition
- `populate.sql` – Initial data population
- `optimiza.sql` – Query optimization scripts
- `actualiza.sql` – Schema and data updates
- `docker-compose.yml` – Container orchestration

## Key Features
- Relational database schema design and normalization
- SQL triggers for automated database logic
- Transaction management and concurrency control
- Containerized backend services using Docker

## How to Run
```bash
docker-compose up --build
