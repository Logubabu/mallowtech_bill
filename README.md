# Billing System

A simple billing application built with FastAPI, PostgreSQL, and vanilla HTML/CSS/JavaScript. The project allows users to create bills, calculate taxes and net prices, and view bill history through a lightweight frontend.

## Features
- Product listing from the database
- Bill creation with tax and balance calculation
- Balance denomination breakdown for change
- Bill history lookup by customer email
- Docker-based setup for database, backend, and frontend
- Automatic product seeding on first startup

## Project Structure
- backend/: FastAPI application, database models, CRUD logic, and schemas
- frontend/: Static HTML/CSS/JS files for the UI
- docker-compose.yml: Runs PostgreSQL, backend, and frontend together
- .env: Local environment configuration for the database

## Prerequisites
- Docker Desktop
- Python 3.9+ (for local non-Docker runs)

## Quick Start with Docker
From the project root, run:

```bash
docker compose up -d --build
```

This will start:
- PostgreSQL at port 5432
- Backend API at http://localhost:8000
- Frontend at http://localhost:8080

## Local Development (without Docker)
### 1. Create and activate a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the database
If you are not using Docker, make sure PostgreSQL is running locally and reachable through the values in [.env](.env).

### 4. Run the backend
```bash
cd backend
python main.py
```

The API will be available at http://localhost:8000.

### 5. Run the frontend
In a separate terminal:
```bash
cd frontend
python -m http.server 8080
```

Open http://localhost:8080 to use the app.

## API Endpoints
- GET /api/products - Get all products
- POST /api/bills - Create a bill
- GET /api/bills - Get bill history by email
- GET /api/bills/{bill_id} - Get a bill by ID
- POST /api/seed - Seed sample products

## Notes
- Sample products are seeded automatically on first startup.
- If a product ID is not found, the backend returns a clear error response.
- The app uses a simple mock invoice email task in the background.
