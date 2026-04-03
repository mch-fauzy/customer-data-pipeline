import logging

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models.customer import Customer
from schemas.customer import CustomerListResponse, CustomerResponse, IngestResponse
from services.ingestion import run_ingestion

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Customer Data Pipeline")


@app.post("/api/ingest", response_model=IngestResponse)
def ingest_data() -> IngestResponse:
    try:
        records_processed = run_ingestion()
        return IngestResponse(
            status="success",
            records_processed=records_processed,
        )
    except Exception:
        logger.exception("Ingestion failed")
        raise HTTPException(
            status_code=500, detail="Ingestion failed. Check server logs."
        )


@app.get("/api/customers", response_model=CustomerListResponse)
def get_customers(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> CustomerListResponse:
    total = db.query(func.count()).select_from(Customer).scalar() or 0
    offset = (page - 1) * limit
    customers = (
        db.query(Customer)
        .order_by(Customer.customer_id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return CustomerListResponse(
        data=[CustomerResponse.model_validate(c) for c in customers],
        total=total,
        page=page,
        limit=limit,
    )


@app.get("/api/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
) -> CustomerResponse:
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return CustomerResponse.model_validate(customer)
