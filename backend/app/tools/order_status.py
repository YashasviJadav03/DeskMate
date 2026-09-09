"""
Order Status Tool — mock order lookup that simulates a REST API call.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta


# ── Mock order database ──────────────────────────────────

_MOCK_ORDERS = {
    "ORD-12345": {
        "order_id": "ORD-12345",
        "status": "Shipped",
        "items": ["Wireless Headphones", "Phone Case"],
        "total": 89.99,
        "ordered_date": "2026-09-01",
        "estimated_delivery": "2026-09-12",
        "tracking_number": "TRK-9876543210",
        "carrier": "FedEx",
    },
    "ORD-67890": {
        "order_id": "ORD-67890",
        "status": "Processing",
        "items": ["Running Shoes (Size 10)"],
        "total": 129.99,
        "ordered_date": "2026-09-08",
        "estimated_delivery": "2026-09-15",
        "tracking_number": None,
        "carrier": None,
    },
    "ORD-11111": {
        "order_id": "ORD-11111",
        "status": "Delivered",
        "items": ["Laptop Stand", "USB-C Hub", "Desk Mat"],
        "total": 174.97,
        "ordered_date": "2026-08-20",
        "estimated_delivery": "2026-08-27",
        "tracking_number": "TRK-1234567890",
        "carrier": "UPS",
    },
    "ORD-22222": {
        "order_id": "ORD-22222",
        "status": "Out for Delivery",
        "items": ["Coffee Maker"],
        "total": 59.99,
        "ordered_date": "2026-09-05",
        "estimated_delivery": "2026-09-10",
        "tracking_number": "TRK-5555555555",
        "carrier": "USPS",
    },
}


# ── Tool schema (for LLM function calling) ──────────────

TOOL_SCHEMA = {
    "name": "check_order_status",
    "description": "Look up the current status of a customer order by order ID. Returns order details including status, items, tracking info, and estimated delivery.",
    "parameters": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "The order ID to look up (e.g., ORD-12345)",
            }
        },
        "required": ["order_id"],
    },
}


# ── Tool implementation ──────────────────────────────────


def check_order_status(order_id: str) -> dict:
    """
    Look up an order by ID.

    Returns order details or an error if not found.
    """
    # Normalize the order ID
    order_id = order_id.strip().upper()
    if not order_id.startswith("ORD-"):
        order_id = f"ORD-{order_id}"

    # Look up in mock database
    order = _MOCK_ORDERS.get(order_id)

    if order is None:
        return {
            "success": False,
            "error": f"Order {order_id} not found. Please check the order ID and try again.",
            "order_id": order_id,
        }

    return {
        "success": True,
        **order,
    }
