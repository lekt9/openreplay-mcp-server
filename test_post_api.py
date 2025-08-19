#!/usr/bin/env python3
"""
Test script for OpenReplay API with POST /sessions/search endpoint
"""

import os
import asyncio
import httpx
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_openreplay_api():
    """Test the OpenReplay API configuration"""
    
    api_url = os.getenv('OPENREPLAY_API_URL', 'https://api.openreplay.com')
    api_key = os.getenv('OPENREPLAY_API_KEY', '')
    project_id = os.getenv('OPENREPLAY_PROJECT_ID', '')
    
    print("OpenReplay API Test (POST /sessions/search)")
    print("=" * 50)
    print(f"API URL: {api_url}")
    print(f"Project ID: {project_id}")
    print(f"API Key: {'***' + api_key[-4:] if len(api_key) > 4 else 'NOT SET'}")
    print("=" * 50)
    
    if not api_key:
        print("❌ Error: OPENREPLAY_API_KEY not set in .env file")
        return
    
    if not project_id:
        print("❌ Error: OPENREPLAY_PROJECT_ID not set in .env file")
        return
    
    # Prepare the request
    url = f"{api_url}/{project_id}/sessions/search"
    
    # Default to last 24 hours
    current_time = int(time.time() * 1000)
    start_time = current_time - (24 * 60 * 60 * 1000)
    
    body = {
        "events": [],
        "filters": [],
        "custom": {},
        "rangeValue": "LAST_24_HOURS",
        "startDate": start_time,
        "endDate": current_time,
        "groupByUser": False,
        "sort": "startTs",
        "order": "desc",
        "strict": False,
        "eventsOrder": "then",
        "limit": 10,
        "page": 1,
        "perPage": 10,
        "tab": "sessions"
    }
    
    print(f"\n🔍 Testing endpoint: POST {url}")
    
    async with httpx.AsyncClient() as client:
        try:
            # Ensure Bearer prefix
            auth_header = api_key
            if not auth_header.startswith('Bearer '):
                auth_header = f'Bearer {auth_header}'
            
            response = await client.post(
                url,
                json=body,
                headers={
                    'Authorization': auth_header,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout=10.0
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                sessions = data.get('sessions', [])
                total = data.get('total', len(sessions))
                    
                print(f"✅ Success! Found {total} sessions")
                
                if sessions:
                    print("\nFirst few sessions:")
                    for i, session in enumerate(sessions[:3], 1):
                        print(f"\n  Session {i}:")
                        print(f"    - Session ID: {session.get('sessionId', 'N/A')}")
                        print(f"    - Duration: {session.get('duration', 0)/1000:.1f} seconds")
                        print(f"    - User ID: {session.get('userId', session.get('userAnonymousId', 'N/A'))}")
                        print(f"    - User UUID: {session.get('userUuid', 'N/A')}")
                        print(f"    - Pages: {session.get('pagesCount', 0)}")
                        print(f"    - Events: {session.get('eventsCount', 0)}")
                        print(f"    - Errors: {session.get('errorsCount', 0)}")
                    
            elif response.status_code == 401:
                print("❌ Error: Unauthorized - Check your API key")
                print(f"   Response: {response.text[:200]}")
            elif response.status_code == 404:
                print("❌ Error: Not Found - Check your API URL and project ID")
                print(f"   Response: {response.text[:200]}")
            else:
                print(f"❌ Error: Unexpected status code")
                print(f"   Response: {response.text[:500]}")
                
        except httpx.TimeoutException:
            print("❌ Error: Request timed out")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_openreplay_api())