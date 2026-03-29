import asyncio
import aiohttp
import time

URL = "http://127.0.0.1:8000/buy"
ADMIN_URL = "http://127.0.0.1:8000/admin/reset"
NUM_REQUESTS = 5000  # Number of concurrent requests

async def reset_stock():
    # Reset the stock to 1000
    async with aiohttp.ClientSession()  as session:
        async with session.post(f"{ADMIN_URL}?count=1000") as response:
            result = await response.json()
            print(f"Stock reset: {result}")

async def buy_item(session, req_id):
    try:
        async with session.post(URL) as response:
            if response.status == 200:
                return "SUCCESS"
            elif response.status == 400:
                return "OUT_OF_STOCK"
            else:
                return f"ERROR_{response.status}"
    except Exception as e:
         return "FAILED_CONNECTION"

async def main():
    print(f"Starting load test with {NUM_REQUESTS} concurrent requests...")
    
    # Reset stock to 1000
    await reset_stock()
    
    # Fire requests concurrently
    async with aiohttp.ClientSession() as session:
        tasks = [buy_item(session, i) for i in range(NUM_REQUESTS)]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
    success_count = results.count("SUCCESS")
    out_of_stock_count = results.count("OUT_OF_STOCK")
    other_errors = len(results) - success_count - out_of_stock_count
    
    print("-" * 30)
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    print(f"Total Requests: {NUM_REQUESTS}")
    print(f"Successful Purchases: {success_count} (Expected: 1000)")
    print(f"Out of Stock: {out_of_stock_count} (Expected: {NUM_REQUESTS - 1000})")
    if other_errors > 0:
        print(f"Other errors/failures: {other_errors}")
    print("-" * 30)
    
    if success_count == 1000:
        print("Concurrency test passed. No race conditions detected.")
    else:
        print("Concurrency test failed. Overselling or underselling occurred.")

if __name__ == "__main__":
    asyncio.run(main())
