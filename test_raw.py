import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    api_url = os.getenv('OPENREPLAY_API_URL', 'https://app.openreplay.com')
    api_key = os.getenv('OPENREPLAY_API_KEY', '')
    project_id = os.getenv('OPENREPLAY_PROJECT_ID', '')
    
    async with httpx.AsyncClient() as client:
        url = f"{api_url}/api/v1/{project_id}/users/test@example.com/sessions"
        response = await client.get(
            url,
            headers={
                'Authorization': api_key,
                'Content-Type': 'application/json'
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Response (first 500 chars):\n{response.text[:500]}")

asyncio.run(test())
