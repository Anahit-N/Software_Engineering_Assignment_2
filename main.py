import os
from fastapi import FastAPI, HTTPException
import redis.asyncio as redis
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = FastAPI(title="High-Throughput Inventory Tracker")

# Redis URL
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Distributed Caching
redis_pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True, max_connections=100)
r = redis.Redis(connection_pool=redis_pool)

ITEM_KEY = "inventory:flash_sale_item"

@app.on_event("startup")
async def startup_event():
    try:
        await r.ping()
        print("Connected to Redis successfully.")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    await r.close()

@app.post("/admin/reset", summary="Admin Reset Inventory")
async def reset_inventory(count: int = 1000):
    # Reset the inventory count.
    await r.set(ITEM_KEY, count)
    return {"message": "Inventory reset successfully.", "current_stock": count}

@app.post("/buy", summary="Attempt to Buy an Item")
async def buy_item():
    """
    Purchase endpoint logic with concurrency control.
    Uses atomic DECR operation to prevent race conditions.
    """
    try:
        # Concurrency
        stock_remaining = await r.decr(ITEM_KEY)
        
        if stock_remaining >= 0:
            return {
                "status": "success", 
                "message": "Item purchased successfully!", 
                "stock_remaining": stock_remaining
            }
        else:
            # Oversold INCR back the value and fail the request
            await r.incr(ITEM_KEY)
            raise HTTPException(status_code=400, detail="Out of Stock")
            
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")

@app.get("/inventory", summary="Get Current Inventory")
async def get_inventory():
    """
    Fetch the current inventory stock level without decrementing.
    """
    stock = await r.get(ITEM_KEY)
    if stock is None:
        return {"stock_remaining": 0}
    return {"stock_remaining": int(stock)}
