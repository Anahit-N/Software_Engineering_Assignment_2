# Assignment 2: High-Throughput Inventory Tracker

FastAPI application implementing a distributed inventory system for a flash-sale. 

**Concurrency Control**: Uses Redis's atomic `DECR` operation to process concurrent decrements safely and prevent overselling race conditions.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the server (defaults to local Redis):
   ```bash
   uvicorn main:app --port 8000
   ```

## Load Testing
The `load_test.py` script sends 5,000 concurrent requests trying to buy 1,000 items to verify concurrency control.

```bash
python load_test.py
```

## API Endpoints
- `GET /inventory` : Fetch current stock.
- `POST /admin/reset?count=1000` : Reset stock.
- `POST /buy` : Attempt purchase.
