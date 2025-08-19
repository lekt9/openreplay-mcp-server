#!/usr/bin/env python3
"""Test various endpoint patterns"""

import asyncio
import httpx
import json

api_key = '5auNKdVzDfvUTjsBEDbf'
project_id = '34vlVhQDDp5g4jhtL15M'
user_id = 'k9742x5h3jbxjx20k52b2dt6th7ng54e'

endpoints_to_test = [
    # Users endpoints (we know these work)
    ("GET", f"/api/v1/{project_id}/users/{user_id}/sessions", None),
    ("GET", f"/api/v1/{project_id}/users/{user_id}", None),
    
    # Try different search patterns
    ("POST", f"/api/v1/{project_id}/sessions/search", {"filters": [], "limit": 10}),
    ("GET", f"/api/v1/{project_id}/sessions", None),
    ("POST", f"/api/v1/sessions/search", {"projectId": project_id, "filters": [], "limit": 10}),
    
    # Try without v1
    ("POST", f"/api/{project_id}/sessions/search", {"filters": [], "limit": 10}),
    ("GET", f"/api/{project_id}/sessions", None),
    
    # Try projects endpoint
    ("GET", "/api/v1/projects", None),
    ("GET", f"/api/v1/projects/{project_id}", None),
]

async def test_endpoints():
    async with httpx.AsyncClient() as client:
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        for method, endpoint, data in endpoints_to_test:
            url = f"https://api.openreplay.com{endpoint}"
            print(f"\n{method} {endpoint}")
            print("-" * 40)
            
            try:
                if method == "GET":
                    response = await client.get(url, headers=headers, timeout=5.0)
                else:
                    response = await client.post(url, headers=headers, json=data, timeout=5.0)
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'json' in content_type:
                        data = response.json()
                        print(f"✅ SUCCESS - JSON response")
                        print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'List response'}")
                        if isinstance(data, dict) and 'data' in data:
                            if isinstance(data['data'], list):
                                print(f"Data items: {len(data['data'])}")
                            elif isinstance(data['data'], dict):
                                print(f"Data keys: {list(data['data'].keys())}")
                    else:
                        print(f"❌ Non-JSON response: {content_type}")
                else:
                    print(f"❌ HTTP {response.status_code}")
                    if response.text:
                        print(f"Response: {response.text[:200]}")
                        
            except Exception as e:
                print(f"❌ Error: {str(e)[:100]}")

if __name__ == "__main__":
    asyncio.run(test_endpoints())