#!/usr/bin/env python3
import sys
import asyncio
import httpx
import time

async def check_health():
    url = "http://localhost:8000/health"
    timeout = 5
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            start_time = time.time()
            response = await client.get(url)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                print(f"✅ Healthcheck passed: {response.status_code} ({elapsed:.2f}s)")
                print(f"📊 Response: {response.text}")
                sys.exit(0)
            else:
                print(f"❌ Healthcheck failed: {response.status_code}")
                print(f"📋 Response: {response.text}")
                sys.exit(1)
    except Exception as e:
        print(f"❌ Healthcheck error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(check_health())
