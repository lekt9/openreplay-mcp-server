#!/usr/bin/env python3
"""Test different authentication methods for OpenReplay API"""

import asyncio
import httpx
import json

async def test_auth_methods():
    api_key = '5auNKdVzDfvUTjsBEDbf'
    project_id = '34vlVhQDDp5g4jhtL15M'
    user_id = 'k9742x5h3jbxjx20k52b2dt6th7ng54e'
    
    # Different possible base URLs
    base_urls = [
        'https://app.openreplay.com',
        'https://api.openreplay.com',
    ]
    
    # Different auth header formats
    auth_formats = [
        ('Authorization', api_key),
        ('Authorization', f'Bearer {api_key}'),
        ('X-API-Key', api_key),
        ('Api-Key', api_key),
        ('x-api-key', api_key),
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for base_url in base_urls:
            print(f"\n{'='*60}")
            print(f"Testing base URL: {base_url}")
            print('='*60)
            
            for header_name, header_value in auth_formats:
                print(f"\nTrying {header_name}: {header_value[:20]}...")
                
                headers = {
                    header_name: header_value,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
                
                # Test endpoint
                url = f"{base_url}/api/v1/{project_id}/users/{user_id}/sessions"
                
                try:
                    response = await client.get(url, headers=headers)
                    print(f"  Status: {response.status_code}")
                    content_type = response.headers.get('content-type', '')
                    print(f"  Content-Type: {content_type}")
                    
                    if response.status_code == 200 and 'json' in content_type:
                        print(f"  ✅ SUCCESS! Found working configuration:")
                        print(f"     Base URL: {base_url}")
                        print(f"     Auth Header: {header_name}: {header_value[:20]}...")
                        data = response.json()
                        print(f"     Response preview: {json.dumps(data, indent=2)[:300]}")
                        return
                    elif response.status_code == 401:
                        print(f"  ❌ Unauthorized")
                    elif response.status_code == 404:
                        print(f"  ❌ Not Found")
                    elif 'html' in content_type:
                        print(f"  ❌ Returns HTML (wrong endpoint or auth)")
                        
                except httpx.ConnectError:
                    print(f"  ❌ Connection failed (URL doesn't exist)")
                except Exception as e:
                    print(f"  ❌ Error: {str(e)[:100]}")
        
        print("\n\nNo working configuration found. The API might:")
        print("1. Require a different authentication method")
        print("2. Use different endpoints than documented")
        print("3. Need additional setup or activation")

if __name__ == "__main__":
    asyncio.run(test_auth_methods())