#!/usr/bin/env python3
"""
Test script for OpenReplay Official API
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
    project_key = os.getenv('OPENREPLAY_PROJECT_KEY', '')
    
    print("OpenReplay Official API Test")
    print("=" * 50)
    print(f"API URL: {api_url}")
    print(f"Project Key: {project_key}")
    print(f"API Key: {'***' + api_key[-4:] if len(api_key) > 4 else 'NOT SET'}")
    print("=" * 50)
    
    if not api_key:
        print("❌ Error: OPENREPLAY_API_KEY not set in .env file")
        print("   Get it from: Preferences > Account > Organization API Key")
        return
    
    if not project_key:
        print("❌ Error: OPENREPLAY_PROJECT_KEY not set in .env file")
        return
    
    async with httpx.AsyncClient() as client:
        # Test 1: List projects
        print("\n📋 Test 1: List Projects")
        try:
            response = await client.get(
                f"{api_url}/api/v1/projects",
                headers={
                    'Authorization': api_key,
                    'Content-Type': 'application/json'
                },
                timeout=10.0
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                projects = data.get('data', [])
                print(f"  ✅ Found {len(projects)} project(s)")
                for proj in projects[:3]:
                    print(f"    - {proj.get('name')}: {proj.get('projectKey')}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        # Test 2: Get sessions for a user
        test_user_id = input("\n📧 Enter a user ID to test (or press Enter to skip): ").strip()
        
        if test_user_id:
            print(f"\n👤 Test 2: Get Sessions for User: {test_user_id}")
            try:
                response = await client.get(
                    f"{api_url}/api/v1/{project_key}/users/{test_user_id}/sessions",
                    headers={
                        'Authorization': api_key,
                        'Content-Type': 'application/json'
                    },
                    timeout=10.0
                )
                print(f"  Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    sessions = data.get('data', [])
                    print(f"  ✅ Found {len(sessions)} session(s)")
                    for session in sessions[:3]:
                        print(f"    - Session {session.get('sessionId')}: {session.get('duration', 0)/1000:.1f}s")
                elif response.status_code == 404:
                    print(f"  ⚠️ User not found or no sessions")
                else:
                    print(f"  ❌ Error: {response.text[:200]}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
            
            # Test 3: Get user stats
            print(f"\n📊 Test 3: Get User Stats")
            try:
                response = await client.get(
                    f"{api_url}/api/v1/{project_key}/users/{test_user_id}",
                    headers={
                        'Authorization': api_key,
                        'Content-Type': 'application/json'
                    },
                    timeout=10.0
                )
                print(f"  Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    user_data = data.get('data', {})
                    print(f"  ✅ User Stats:")
                    print(f"    - Session Count: {user_data.get('sessionCount', 0)}")
                    print(f"    - First Seen: {user_data.get('firstSeen', 'N/A')}")
                    print(f"    - Last Seen: {user_data.get('lastSeen', 'N/A')}")
            except Exception as e:
                print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_openreplay_api())