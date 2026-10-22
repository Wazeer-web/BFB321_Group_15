
"""
Economic Order Quantity (EOQ) model for the Kopano inventory project.

This module is independent of the frontend, database and web framework.

Assumptions:
- Annual demand is known and constant.
- Ordering cost per order is constant.
- Annual holding cost per unit is constant and positive.
- The model calculates ordering and holding costs, excluding purchase cost.
"""


def _validate_positive_number(value, name):
    """Raise ValueError if value is not a positive finite number."""
    import math

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number.")

    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be greater than zero.")


def calculate_eoq(demand, order_cost, hold_cost):
    """
    Calculate the Economic Order Quantity.

    Formula:
        EOQ = sqrt((2 * D * S) / H)

    Args:
        demand: Annual demand in units per year.
        order_cost: Ordering cost in currency per order.
        hold_cost: Holding cost in currency per unit per year.

    Returns:
        Optimal order quantity in units.
    """
    import math

    _validate_positive_number(demand, "demand")
    _validate_positive_number(order_cost, "order_cost")
    _validate_positive_number(hold_cost, "hold_cost")

    return math.sqrt((2 * demand * order_cost) / hold_cost)


def orders_per_year(demand, order_quantity):
    """
    Calculate the expected number of orders per year.

    Formula:
        Orders per year = annual demand / order quantity
    """
    _validate_positive_number(demand, "demand")
    _validate_positive_number(order_quantity, "order_quantity")

    return demand / order_quantity


def total_annual_cost(demand, order_cost, hold_cost, order_quantity):
    """
    Calculate annual ordering plus holding costs.

    Formula:
        Total cost = (D / Q) * S + (Q / 2) * H

    Purchase cost and shortage costs are excluded.
    """
    _validate_positive_number(demand, "demand")
    _validate_positive_number(order_cost, "order_cost")
    _validate_positive_number(hold_cost, "hold_cost")
    _validate_positive_number(order_quantity, "order_quantity")

    ordering_cost_total = (demand / order_quantity) * order_cost
    holding_cost_total = (order_quantity / 2) * hold_cost

    return ordering_cost_total + holding_cost_total
