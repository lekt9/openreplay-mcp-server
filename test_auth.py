import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    api_key = os.getenv('OPENREPLAY_API_KEY', '')
    project_id = os.getenv('OPENREPLAY_PROJECT_ID', '')
    
    # Try different URL patterns
    test_urls = [
        f"https://api.openreplay.com/v1/{project_id}/users/test@example.com/sessions",
        f"https://app.openreplay.com/api/{project_id}/users/test@example.com/sessions",
        f"https://app.openreplay.com/v1/{project_id}/users/test@example.com/sessions",
        f"https://api.app.openreplay.com/v1/{project_id}/users/test@example.com/sessions",
    ]
    
    async with httpx.AsyncClient() as client:
        for url in test_urls:
            print(f"\nTrying: {url}")
            try:
                response = await client.get(
                    url,
                    headers={
                        'Authorization': api_key,
                        'Content-Type': 'application/json'
                    },
                    timeout=5.0
                )
                print(f"  Status: {response.status_code}")
                print(f"  Content-Type: {response.headers.get('content-type')}")
                if 'json' in response.headers.get('content-type', ''):
                    print(f"  JSON Response: {response.json()}")
            except Exception as e:
                print(f"  Error: {e}")

asyncio.run(test())
