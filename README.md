# Customer Data Pipeline

A data pipeline with 3 Docker services that ingests customer data from a mock server into PostgreSQL.

## Architecture

```
Flask (JSON) → FastAPI (dlt Ingest) → PostgreSQL → API Response
```

- **Flask Mock Server** (port 5000): Serves customer data from JSON file
- **FastAPI Pipeline** (port 8000): Ingests data using dlt, serves from PostgreSQL
- **PostgreSQL** (port 5432): Persistent data storage

## Prerequisites

- Docker Desktop (running)
- Python 3.10+
- Git

## Quick Start

```bash
# Start all services
docker compose up -d

# Verify services are running
docker compose ps

# Check Flask health
curl http://localhost:5000/api/health

# Trigger FastAPI to ingest data from Flask into PostgreSQL
curl -X POST http://localhost:8000/api/ingest
```

## API Endpoints

### Flask Mock Server (port 5000)

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check |
| `/api/customers?page=1&limit=10` | GET | Paginated customer list |
| `/api/customers/{id}` | GET | Single customer by ID |

### FastAPI Pipeline (port 8000)

| Endpoint | Method | Description |
|---|---|---|
| `/api/ingest` | POST | Ingest data from Flask into PostgreSQL |
| `/api/customers?page=1&limit=10` | GET | Paginated customers from database |
| `/api/customers/{id}` | GET | Single customer from database |

## Interactive API Docs (Swagger UI)

- **Flask Mock Server**: http://localhost:5000/docs
- **FastAPI Pipeline**: http://localhost:8000/docs

Both services provide interactive Swagger UI where you can test all endpoints directly from the browser.

## Testing

```bash
# Get customers from Flask mock server
curl "http://localhost:5000/api/customers?page=1&limit=5"

# Trigger data ingestion
curl -X POST http://localhost:8000/api/ingest

# Get customers from PostgreSQL via FastAPI
curl "http://localhost:8000/api/customers?page=1&limit=5"

# Get single customer
curl http://localhost:8000/api/customers/CUST001
```

## Stop Services

```bash
docker compose down
```
