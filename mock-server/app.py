import json
import logging
import os
from typing import TypedDict

from flasgger import Swagger
from flask import Flask, Response, jsonify, request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


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


MAX_LIMIT = 100

app = Flask(__name__)
app.json.sort_keys = False

app.config["SWAGGER"] = {"uiversion": 3, "specs_route": "/docs/"}
Swagger(app, template={
    "info": {
        "title": "Customer Mock Server",
        "description": "Mock REST API serving customer data from JSON file",
        "version": "1.0.0",
    },
})

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "customers.json")

try:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        CUSTOMERS: list[CustomerDict] = json.load(f)
except FileNotFoundError:
    raise RuntimeError(f"Customer data file not found: {DATA_PATH}") from None
except json.JSONDecodeError as exc:
    raise RuntimeError(f"Invalid JSON in customer data file: {exc}") from exc

CUSTOMERS_BY_ID: dict[str, CustomerDict] = {
    c["customer_id"]: c for c in CUSTOMERS
}


@app.route("/api/health", methods=["GET"])
def health() -> Response:
    """Health check
    ---
    responses:
      200:
        description: Service is healthy
    """
    return jsonify({"status": "healthy"})


@app.route("/api/customers", methods=["GET"])
def get_customers() -> Response:
    """Get paginated customer list
    ---
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: Page number (1-indexed)
      - name: limit
        in: query
        type: integer
        default: 10
        description: Records per page (max 100)
    responses:
      200:
        description: Paginated customer list
    """
    page = max(1, request.args.get("page", 1, type=int))
    limit = min(max(1, request.args.get("limit", 10, type=int)), MAX_LIMIT)

    start = (page - 1) * limit
    end = start + limit
    paginated = CUSTOMERS[start:end]

    return jsonify({
        "data": paginated,
        "total": len(CUSTOMERS),
        "page": page,
        "limit": limit,
    })


@app.route("/api/customers/<customer_id>", methods=["GET"])
def get_customer(customer_id: str) -> tuple[Response, int] | Response:
    """Get single customer by ID
    ---
    parameters:
      - name: customer_id
        in: path
        type: string
        required: true
        description: Customer ID (e.g. CUST001)
    responses:
      200:
        description: Customer found
      404:
        description: Customer not found
    """
    customer = CUSTOMERS_BY_ID.get(customer_id)
    if customer:
        return jsonify(customer)
    return jsonify({"error": "Customer not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
