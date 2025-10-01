"""
Test async aiohttp connection to Polygon API
"""

import asyncio
import aiohttp

async def test_async_polygon():
    """Test if async aiohttp can connect to Polygon"""
    api_key = "_u0zA0CH5ZspOHecb2G8uBxd2DUo4r9D"
    url = f"https://api.polygon.io/v2/aggs/ticker/SPY/prev?adjusted=true&apiKey={api_key}"

    print("Testing async aiohttp connection to Polygon...")

    try:
        async with aiohttp.ClientSession() as session:
            print(f"Session created: {session}")

            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                print(f"✅ Connection successful!")
                print(f"Status: {response.status}")

                if response.status == 200:
                    data = await response.json()
                    if 'results' in data:
                        result = data['results'][0]
                        print(f"SPY Close: ${result['c']:.2f}")
                        return True

    except aiohttp.ClientConnectorError as e:
        print(f"❌ Connection Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_async_polygon())
    print(f"\nResult: {'SUCCESS' if result else 'FAILED'}")
