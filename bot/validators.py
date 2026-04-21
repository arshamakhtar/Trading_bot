"""
validators.py
Validates and normalises CLI input before anything touches the Binance API.
Raises ValueError with a human-readable message on bad input.
"""

from decimal import Decimal, InvalidOperation
from typing import Optional


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def validate_symbol(symbol: str) -> str:
    """Return upper-cased symbol; raise if blank."""
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("symbol cannot be empty.")
    if not symbol.isalnum():
        raise ValueError(f"symbol must be alphanumeric (e.g. BTCUSDT). Got: {symbol!r}")
    return symbol


def validate_side(side: str) -> str:
    """Return upper-cased side; raise if not BUY/SELL."""
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"side must be one of {VALID_SIDES}. Got: {side!r}")
    return side


def validate_order_type(order_type: str) -> str:
    """Return upper-cased order type; raise if unsupported."""
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"order_type must be one of {VALID_ORDER_TYPES}. Got: {order_type!r}"
        )
    return order_type


def validate_quantity(quantity: str) -> str:
    """
    Return quantity as a plain string (Binance expects strings for precision).
    Raises if non-positive or not a valid decimal.
    """
    try:
        qty = Decimal(str(quantity).strip())
    except InvalidOperation:
        raise ValueError(f"quantity must be a positive number. Got: {quantity!r}")
    if qty <= 0:
        raise ValueError(f"quantity must be greater than zero. Got: {qty}")
    return str(qty)


def validate_price(price: Optional[str], order_type: str) -> Optional[str]:
    """
    For LIMIT orders price is required and must be positive.
    For MARKET orders price must be None/omitted.
    Returns a plain string or None.
    """
    if order_type == "LIMIT":
        if price is None or str(price).strip() == "":
            raise ValueError("price is required for LIMIT orders.")
        try:
            p = Decimal(str(price).strip())
        except InvalidOperation:
            raise ValueError(f"price must be a positive number. Got: {price!r}")
        if p <= 0:
            raise ValueError(f"price must be greater than zero. Got: {p}")
        return str(p)

    # MARKET order — price must NOT be sent
    if price is not None and str(price).strip() != "":
        raise ValueError("price must not be provided for MARKET orders.")
    return None


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
) -> dict:
    """
    Run all validators and return a clean dict ready for order placement.
    Raises ValueError on the first problem found.
    """
    clean_symbol = validate_symbol(symbol)
    clean_side = validate_side(side)
    clean_type = validate_order_type(order_type)
    clean_qty = validate_quantity(quantity)
    clean_price = validate_price(price, clean_type)

    result = {
        "symbol": clean_symbol,
        "side": clean_side,
        "order_type": clean_type,
        "quantity": clean_qty,
    }
    if clean_price is not None:
        result["price"] = clean_price

    return result
