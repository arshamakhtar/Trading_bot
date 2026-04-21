"""
orders.py
Orchestrates order placement: validates inputs, calls the client,
prints a formatted summary to the terminal, and logs everything.
"""

from typing import Optional

from bot.client import BinanceFuturesClient, BinanceFuturesClientError
from bot.logging_config import setup_logger
from bot.validators import validate_all

logger = setup_logger("trading_bot.orders")


# ── Pretty-printing helpers ──────────────────────────────────────────────────

def _print_request_summary(params: dict) -> None:
    print("\n" + "=" * 52)
    print("   ORDER REQUEST SUMMARY")
    print("=" * 52)
    for key, value in params.items():
        print(f"   {key:<16}: {value}")
    print("=" * 52)


def _print_response_summary(response: dict) -> None:
    print("\n" + "=" * 52)
    print("   ORDER RESPONSE")
    print("=" * 52)

    # Fields of interest — Binance Spot order response
    fields = [
        ("orderId",      "Order ID"),
        ("status",       "Status"),
        ("executedQty",  "Executed Qty"),
        ("cummulativeQuoteQty", "Filled Quote"),
        ("symbol",       "Symbol"),
        ("side",         "Side"),
        ("type",         "Type"),
        ("origQty",      "Original Qty"),
        ("price",        "Price"),
        ("timeInForce",  "Time In Force"),
        ("transactTime", "Transact Time"),
    ]

    for field, label in fields:
        value = response.get(field)
        if value is not None and value != "":
            print(f"   {label:<16}: {value}")

    # avgPrice is Futures-only; Spot MARKET fills are in the 'fills' array
    fills = response.get("fills", [])
    if fills:
        total_qty   = sum(float(f["qty"])   for f in fills)
        total_quote = sum(float(f["qty"]) * float(f["price"]) for f in fills)
        avg_price   = total_quote / total_qty if total_qty else 0
        print(f"   {'Avg Fill Price':<16}: {avg_price:.8f}")

    print("=" * 52)


# ── Main entry point ─────────────────────────────────────────────────────────

def place_order(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
) -> None:
    """
    Validate inputs, place the order, and print + log results.
    All exceptions are handled; the caller always gets a clean message.
    """
    # 1. Validate
    try:
        clean = validate_all(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
        )
    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        print(f"\n[ERROR] Invalid input: {exc}")
        return

    logger.info(
        "Placing %s %s order | symbol=%s qty=%s%s",
        clean["side"], clean["order_type"], clean["symbol"], clean["quantity"],
        f" price={clean['price']}" if "price" in clean else "",
    )
    _print_request_summary(clean)

    # 2. Initialise client
    try:
        client = BinanceFuturesClient()
    except EnvironmentError as exc:
        logger.error("Client init failed: %s", exc)
        print(f"\n[ERROR] {exc}")
        return

    # 3. Connectivity check
    if not client.ping():
        msg = "Cannot reach Binance Spot Testnet (testnet.binance.vision). Check your connection."
        logger.error(msg)
        print(f"\n[ERROR] {msg}")
        return

    # 4. Place order
    try:
        response = client.place_order(
            symbol=clean["symbol"],
            side=clean["side"],
            order_type=clean["order_type"],
            quantity=clean["quantity"],
            price=clean.get("price"),
        )
    except BinanceFuturesClientError as exc:
        logger.error("Order placement failed (API error): %s", exc)
        print(f"\n[FAILED] Binance API returned an error:\n   {exc}")
        return
    except Exception as exc:
        logger.exception("Unexpected error during order placement: %s", exc)
        print(f"\n[FAILED] Unexpected error: {exc}")
        return

    # 5. Print and log success
    _print_response_summary(response)
    logger.info(
        "Order placed successfully | orderId=%s status=%s executedQty=%s",
        response.get("orderId"),
        response.get("status"),
        response.get("executedQty"),
    )
    print("\n[SUCCESS] Order placed successfully.")
