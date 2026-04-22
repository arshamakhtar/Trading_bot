# Binance Spot Testnet Trading Bot

A minimal Python CLI to place **MARKET** and **LIMIT** orders on the
[Binance Spot Test Network](https://testnet.binance.vision).


---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST client (HMAC-SHA256 signing, HTTP, errors)
│   ├── orders.py          # Order orchestration + terminal output
│   ├── validators.py      # Input validation (symbol, side, type, qty, price)
│   └── logging_config.py  # File + console logger setup
├── cli.py                 # argparse entry point
├── logs/
│   └── trading_bot.log    # Auto-created on first run
├── .env.example           # Credential template — copy to .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone or unzip the project

```bash
cd trading_bot
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure your Binance Spot Testnet credentials

```bash
cp .env.example .env
```

Edit `.env`:

```
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

**How to get credentials:**
1. Visit [https://testnet.binance.vision](https://testnet.binance.vision)
2. Log in with GitHub → click **API Management** → generate a key pair
3. Paste the key and secret into `.env`

> `.env` is listed in `.gitignore` — your secrets will never be committed.

---

## How to Run

### MARKET BUY

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### LIMIT SELL

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 99500
```

### Short flags

```bash
python cli.py -s BTCUSDT -S BUY -t MARKET -q 0.001
python cli.py -s BTCUSDT -S SELL -t LIMIT  -q 0.001 -p 99500
```

### Help

```bash
python cli.py --help
```

---

## Example Terminal Output

**MARKET BUY:**

```
====================================================
   ORDER REQUEST SUMMARY
====================================================
   symbol          : BTCUSDT
   side            : BUY
   order_type      : MARKET
   quantity        : 0.001
====================================================

====================================================
   ORDER RESPONSE
====================================================
   Order ID        : 4614911523
   Status          : FILLED
   Executed Qty    : 0.001
   Filled Quote    : 97.842300
   Symbol          : BTCUSDT
   Side            : BUY
   Type            : MARKET
   Original Qty    : 0.001
   Avg Fill Price  : 97842.30000000
====================================================

[SUCCESS] Order placed successfully.
```

**LIMIT SELL:**

```
====================================================
   ORDER REQUEST SUMMARY
====================================================
   symbol          : BTCUSDT
   side            : SELL
   order_type      : LIMIT
   quantity        : 0.001
   price           : 99500
====================================================

====================================================
   ORDER RESPONSE
====================================================
   Order ID        : 4614912087
   Status          : NEW
   Executed Qty    : 0.00000000
   Symbol          : BTCUSDT
   Side            : SELL
   Type            : LIMIT
   Original Qty    : 0.001
   Price           : 99500.00000000
   Time In Force   : GTC
====================================================

[SUCCESS] Order placed successfully.
```

---

## Logging

All requests, responses, and errors are logged to `logs/trading_bot.log`.
The log directory is created automatically on first run.

```
2025-07-14 10:22:11 | DEBUG    | trading_bot.client | POST /api/v3/order | params={...}
2025-07-14 10:22:12 | DEBUG    | trading_bot.client | HTTP 200 | response: {...}
2025-07-14 10:22:12 | INFO     | trading_bot.orders | Order placed successfully | orderId=... status=FILLED
```

> API signatures are never logged. The key appears only as its last 6 characters.

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Missing `.env` credentials | EnvironmentError before any network call |
| Invalid side / type / symbol | ValueError — no API call made |
| LIMIT order without price | ValueError — no API call made |
| MARKET order with price | ValueError — no API call made |
| Quantity ≤ 0 | ValueError — no API call made |
| Binance API error (4xx) | Prints Binance error code + message |
| Network / timeout failure | Descriptive error printed + logged |

---

## API Target

| Setting | Value |
|---|---|
| Network | Binance Spot Test Network |
| Base URL | `https://testnet.binance.vision` |
| Order endpoint | `POST /api/v3/order` |
| Auth method | HMAC-SHA256 signed timestamp + recvWindow |

---

## Dependencies

```
requests>=2.31.0
python-dotenv>=1.0.0
```
