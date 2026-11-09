from langchain_core.tools import tool


@tool
def get_order_status(order_id: str) -> dict:
    """Get the current status of a customer order using its order ID."""

    orders = {
        "ORD-1024": {
            "status": "shipped",
            "estimated_delivery": "2026-11-12",
        },
        "ORD-1025": {
            "status": "processing",
            "estimated_delivery": "2026-11-15",
        },
    }

    return orders.get(order_id, {"error": "Order not found"})


@tool
def check_refund_eligibility(order_id: str) -> dict:
    """Check whether a customer is eligible for a refund."""

    orders = {
        "ORD-1024": {
            "eligible": False,
            "reason": "Order has already been shipped.",
        },
        "ORD-1025": {
            "eligible": True,
            "reason": "Order is still processing.",
        },
    }

    return orders.get(order_id, {"error": "Order not found"})


tools = [
    get_order_status,
    check_refund_eligibility,
]

tools_by_name = {
    tool.name: tool
    for tool in tools
}