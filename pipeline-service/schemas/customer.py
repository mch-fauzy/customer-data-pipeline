from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: str
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    address: str | None = None
    date_of_birth: date | None = None
    account_balance: Decimal | None = None
    created_at: datetime | None = None


class CustomerListResponse(BaseModel):
    data: list[CustomerResponse]
    total: int
    page: int
    limit: int


class IngestResponse(BaseModel):
    status: Literal["success"]
    records_processed: int
