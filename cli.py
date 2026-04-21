"""
cli.py
Command-line entry point for the Binance Futures Testnet trading bot.

Usage examples:

  # MARKET BUY
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  # LIMIT SELL
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000

  # Short flags
  python cli.py -s BTCUSDT -S BUY -t MARKET -q 0.001
"""

import argparse
import sys
from pathlib import Path

# Allow running directly from the project root without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bot.logging_config import setup_logger
from bot.orders import place_order

logger = setup_logger("trading_bot.cli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance Futures Testnet (USDT-M).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --symbol BTCUSDT --side BUY  --type MARKET --quantity 0.001
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT  --quantity 0.001 --price 70000
        """,
    )

    parser.add_argument(
        "-s", "--symbol",
        required=True,
        metavar="SYMBOL",
        help="Trading pair symbol, e.g. BTCUSDT",
    )
    parser.add_argument(
        "-S", "--side",
        required=True,
        metavar="SIDE",
        choices=["BUY", "SELL", "buy", "sell"],
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "-t", "--type",
        required=True,
        dest="order_type",
        metavar="TYPE",
        choices=["MARKET", "LIMIT", "market", "limit"],
        help="Order type: MARKET or LIMIT",
    )
    parser.add_argument(
        "-q", "--quantity",
        required=True,
        metavar="QTY",
        help="Order quantity (positive decimal)",
    )
    parser.add_argument(
        "-p", "--price",
        required=False,
        default=None,
        metavar="PRICE",
        help="Limit price (required for LIMIT orders, must not be set for MARKET)",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logger.info(
        "CLI invoked | symbol=%s side=%s type=%s qty=%s price=%s",
        args.symbol,
        args.side,
        args.order_type,
        args.quantity,
        args.price,
    )

    place_order(
        symbol=args.symbol,
        side=args.side,
        order_type=args.order_type,
        quantity=args.quantity,
        price=args.price,
    )


if __name__ == "__main__":
    main()
