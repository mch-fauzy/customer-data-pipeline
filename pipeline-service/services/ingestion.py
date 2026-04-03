import logging
import os
from collections.abc import Iterator
from typing import TypedDict

import dlt
import requests

from database import DATABASE_URL

logger = logging.getLogger(__name__)

FETCH_PAGE_SIZE = 100


class CustomerDict(TypedDict):
    customer_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    date_of_birth: str
    account_balance: float
    created_at: str


MOCK_SERVER_URL = os.environ.get("MOCK_SERVER_URL", "http://mock-server:5000")


@dlt.resource(
    name="customers",
    write_disposition="merge",
    primary_key="customer_id",
)
def fetch_customers() -> Iterator[list[CustomerDict]]:
    page = 1

    while True:
        try:
            response = requests.get(
                f"{MOCK_SERVER_URL}/api/customers",
                params={"page": page, "limit": FETCH_PAGE_SIZE},
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            logger.error("Failed to fetch page %d: %s", page, exc)
            raise

        records = payload.get("data", [])
        total = payload.get("total", 0)

        if not records:
            break

        yield records

        fetched_so_far = (page - 1) * FETCH_PAGE_SIZE + len(records)
        if fetched_so_far >= total:
            break

        page += 1


def run_ingestion() -> int:
    pipeline = dlt.pipeline(
        pipeline_name="customer_pipeline",
        destination=dlt.destinations.postgres(credentials=DATABASE_URL),
        dataset_name="public",
    )

    load_info = pipeline.run(fetch_customers())
    load_info.raise_on_failed_jobs()

    normalize_info = pipeline.last_trace.last_normalize_info
    if normalize_info is None:
        return 0
    row_counts = normalize_info.row_counts
    logger.debug("dlt row_counts: %s", row_counts)
    return row_counts.get("customers", 0)
