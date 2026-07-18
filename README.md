# Billing System

This is a mini project built with FastAPI, PostgreSQL, and Vanilla HTML/JS.

## Features
- **Database Schema**: Products with fields (`name`, `product_id`, `available_stocks`, `price`, `tax_percentage`).
- **Billing API**: Create a bill, calculate taxes and net prices, check balance payable, and calculate denominations.
- **Background Tasks**: Sends an invoice asynchronously (mocked with an async sleep & print).
- **Frontend**: Clean Vanilla HTML/JS implementation as requested.
- **Dockerized Database**: Easy setup via docker-compose.

## Prerequisites
- Docker (for PostgreSQL)
- Python 3.9+

## Setup & Running the Project

### 1. Database Setup
Start the PostgreSQL database using Docker:
```bash
docker-compose up -d
```

### 2. Backend Setup
Navigate to the `backend` folder, install requirements, and run the server:
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
The FastAPI backend will run at `http://localhost:8000`.

### 3. Seed Database
Open your browser or use `curl` to hit the seed endpoint to add initial products:
[http://localhost:8000/api/seed](http://localhost:8000/api/seed)

*Seeded Products:*
- `P001`: Product A (Price: 100, Tax: 5%)
- `P002`: Product B (Price: 50, Tax: 12%)
- `P003`: Product C (Price: 10, Tax: 18%)

### 4. Frontend Setup
Navigate to the `frontend` folder and serve the HTML files. You can simply open `index.html` in your browser, or serve it using Python:
```bash
cd frontend
python -m http.server 8080
```
Open [http://localhost:8080](http://localhost:8080) to interact with the billing system.

## Assumptions
- It's assumed the shop always has enough denominations to provide change. The system returns the optimal change (largest denominations first).
- The invoice sending mechanism is a mock function that uses `asyncio.sleep` to simulate a background task and prints the email log to the backend console.
- Basic validation is applied (e.g., checking if cash paid >= net amount).
