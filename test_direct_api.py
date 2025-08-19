#!/usr/bin/env python3
"""Direct API testing for OpenReplay"""

import os
import asyncio
import httpx
import json

async def test_apis():
    # Your credentials
    api_key = '5auNKdVzDfvUTjsBEDbf'
    project_id = '34vlVhQDDp5g4jhtL15M'
    api_url = 'https://app.openreplay.com'
    user_id = 'k9742x5h3jbxjx20k52b2dt6th7ng54e'
    
    print("Testing OpenReplay APIs Directly")
    print("=" * 60)
    print(f"API Key: ***{api_key[-4:]}")
    print(f"Project ID: {project_id}")
    print(f"User ID: {user_id}")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }
        
        # Test 1: Get user sessions
        print("\n1. Testing GET /api/v1/{project}/users/{user}/sessions")
        url = f"{api_url}/api/v1/{project_id}/users/{user_id}/sessions"
        print(f"   URL: {url}")
        
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'None')}")
            
            if 'json' in response.headers.get('content-type', ''):
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:500]}")
            else:
                print(f"   Response (first 200 chars): {response.text[:200]}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 2: Get user details
        print("\n2. Testing GET /api/v1/{project}/users/{user}")
        url = f"{api_url}/api/v1/{project_id}/users/{user_id}"
        print(f"   URL: {url}")
        
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'None')}")
            
            if 'json' in response.headers.get('content-type', ''):
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:500]}")
            else:
                print(f"   Response (first 200 chars): {response.text[:200]}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 3: Try without project ID (list all projects)
        print("\n3. Testing GET /api/v1/projects")
        url = f"{api_url}/api/v1/projects"
        print(f"   URL: {url}")
        
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'None')}")
            
            if 'json' in response.headers.get('content-type', ''):
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:500]}")
            else:
                print(f"   Response (first 200 chars): {response.text[:200]}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 4: Try Bearer token format
        print("\n4. Testing with Bearer token format")
        headers_bearer = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        url = f"{api_url}/api/v1/{project_id}/users/{user_id}/sessions"
        print(f"   URL: {url}")
        
        try:
            response = await client.get(url, headers=headers_bearer, timeout=10.0)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'None')}")
            
            if 'json' in response.headers.get('content-type', ''):
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:500]}")
            else:
                print(f"   Response (first 200 chars): {response.text[:200]}")
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_apis())