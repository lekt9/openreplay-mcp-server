#!/usr/bin/env python3
"""Test OpenReplay API connection with provided credentials"""

import os
import asyncio
import httpx

async def test_connection():
    # Set credentials
    os.environ['OPENREPLAY_API_KEY'] = '5auNKdVzDfvUTjsBEDbf'
    os.environ['OPENREPLAY_PROJECT_ID'] = '34vlVhQDDp5g4jhtL15M'
    
    api_url = 'https://app.openreplay.com'
    api_key = os.environ['OPENREPLAY_API_KEY']
    project_id = os.environ['OPENREPLAY_PROJECT_ID']
    
    print("Testing OpenReplay API Connection")
    print("=" * 50)
    print(f"API URL: {api_url}")
    print(f"Project ID: {project_id}")
    print(f"API Key: ***{api_key[-4:]}")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test getting sessions for the user
        user_id = 'k9742x5h3jbxjx20k52b2dt6th7ng54e'
        print(f"\nTesting user sessions endpoint for user: {user_id}")
        
        try:
            # Try the official API endpoint structure
            url = f"{api_url}/api/v1/{project_id}/users/{user_id}/sessions"
            print(f"URL: {url}")
            
            response = await client.get(
                url,
                headers={
                    'Authorization': api_key,
                    'Content-Type': 'application/json'
                },
                timeout=10.0
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Text (first 500 chars): {response.text[:500]}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Successfully parsed JSON")
                    print(f"Response structure: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                except Exception as e:
                    print(f"❌ JSON parsing error: {e}")
            else:
                print(f"❌ Non-200 status code")
                
        except Exception as e:
            print(f"❌ Request error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())