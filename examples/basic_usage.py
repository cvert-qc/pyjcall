import asyncio
import os
from pyjcall import JustCallClient

async def main():
    async with JustCallClient(
        api_key=os.getenv("JUSTCALL_API_KEY"),
        api_secret=os.getenv("JUSTCALL_API_SECRET")
    ) as client:
        # List calls
        calls = await client.Calls.list(per_page=20)
        print(f"Retrieved {len(calls.get('data', []))} calls")

if __name__ == "__main__":
    asyncio.run(main())
