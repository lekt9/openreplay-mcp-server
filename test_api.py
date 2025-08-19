#!/usr/bin/env python3
"""
Test script for OpenReplay API configuration
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_openreplay_api():
    """Test the OpenReplay API configuration"""
    
    api_url = os.getenv('OPENREPLAY_API_URL', 'https://app.openreplay.com')
    api_key = os.getenv('OPENREPLAY_API_KEY', '')
    project_id = os.getenv('OPENREPLAY_PROJECT_ID', '')
    
    print("OpenReplay API Test")
    print("=" * 50)
    print(f"API URL: {api_url}")
    print(f"Project ID: {project_id}")
    print(f"API Key: {'***' + api_key[-4:] if api_key else 'NOT SET'}")
    print("=" * 50)
    
    if not api_key:
        print("❌ Error: OPENREPLAY_API_KEY not set in .env file")
        return
    
    if not project_id:
        print("❌ Error: OPENREPLAY_PROJECT_ID not set in .env file")
        return
    
    # Test with a sample user ID
    test_user_id = input("\nEnter a user ID to test (e.g., email or user ID from your app): ").strip()
    
    if not test_user_id:
        print("❌ Error: User ID is required")
        return
    
    print(f"\n📡 Testing API with user ID: {test_user_id}")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test the sessions endpoint
            url = f"{api_url}/api/v1/{project_id}/users/{test_user_id}/sessions"
            print(f"\n🔍 Testing endpoint: {url}")
            
            response = await client.get(
                url,
                headers={
                    'Authorization': api_key,
                    'Content-Type': 'application/json'
                },
                timeout=10.0
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle both list and dict response formats
                if isinstance(data, list):
                    sessions = data
                else:
                    sessions = data.get('sessions', data.get('data', []))
                    
                print(f"✅ Success! Found {len(sessions)} sessions for user {test_user_id}")
                
                if sessions:
                    print("\nFirst session details:")
                    session = sessions[0]
                    print(f"  - Session ID: {session.get('sessionId', 'N/A')}")
                    print(f"  - Duration: {session.get('duration', 0)/1000:.1f} seconds")
                    print(f"  - User Agent: {session.get('userAgent', 'N/A')[:50]}...")
                    print(f"  - Start Time: {session.get('startTs', 'N/A')}")
                    
            elif response.status_code == 401:
                print("❌ Error: Unauthorized - Check your API key")
            elif response.status_code == 404:
                print("❌ Error: Not Found - Check your API URL and project ID")
                print(f"   Response: {response.text[:200]}")
            else:
                print(f"❌ Error: Unexpected status code")
                print(f"   Response: {response.text[:200]}")
                
        except httpx.TimeoutException:
            print("❌ Error: Request timed out")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_openreplay_api())