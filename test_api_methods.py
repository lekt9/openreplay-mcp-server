#!/usr/bin/env python3
"""Test API client methods"""

import asyncio
import os

# Set environment variables
os.environ['OPENREPLAY_API_KEY'] = '5auNKdVzDfvUTjsBEDbf'
os.environ['OPENREPLAY_PROJECT_ID'] = '34vlVhQDDp5g4jhtL15M'

from openreplay_mcp_server import OpenReplayClient, OpenReplayConfig

async def test_api_methods():
    """Test each API client method"""
    
    config = OpenReplayConfig()
    client = OpenReplayClient(config)
    
    print("Testing API Client Methods")
    print("=" * 60)
    
    test_results = {}
    
    # Test 1: Get user sessions (we know this works)
    try:
        print("\n1. Testing get_user_sessions...")
        result = await client.get_user_sessions('k9742x5h3jbxjx20k52b2dt6th7ng54e')
        sessions = result.get('data', [])
        print(f"   ✅ SUCCESS: Found {len(sessions)} sessions")
        test_results['get_user_sessions'] = True
        
        # Save session ID for other tests
        session_id = sessions[0]['sessionId'] if sessions else None
        
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        test_results['get_user_sessions'] = False
        session_id = None
    
    # Test 2: Get user stats
    try:
        print("\n2. Testing get_user_stats...")
        result = await client.get_user_stats('k9742x5h3jbxjx20k52b2dt6th7ng54e')
        user_data = result.get('data', {})
        print(f"   ✅ SUCCESS: User has {user_data.get('sessionCount', 0)} sessions")
        test_results['get_user_stats'] = True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        test_results['get_user_stats'] = False
    
    # Test 3: Search sessions (might fail - not in public API)
    try:
        print("\n3. Testing search_sessions...")
        result = await client.search_sessions(
            filters=[{
                "is_event": False,
                "type": "userId",
                "operator": "is",
                "value": ["k9742x5h3jbxjx20k52b2dt6th7ng54e"]
            }],
            limit=5
        )
        sessions = result.get('data', {}).get('sessions', [])
        print(f"   ✅ SUCCESS: Found {len(sessions)} sessions")
        test_results['search_sessions'] = True
    except Exception as e:
        if "404" in str(e):
            print(f"   ⚠️ EXPECTED FAIL: Search endpoint not available in public API")
        else:
            print(f"   ❌ FAILED: {e}")
        test_results['search_sessions'] = False
    
    # Test 4: Get session replay (if we have a session)
    if session_id:
        try:
            print(f"\n4. Testing get_session_replay with session {session_id}...")
            result = await client.get_session_replay(session_id)
            print(f"   ✅ SUCCESS: Got replay data")
            test_results['get_session_replay'] = True
        except Exception as e:
            if "404" in str(e):
                print(f"   ⚠️ EXPECTED FAIL: Replay endpoint might not be available")
            else:
                print(f"   ❌ FAILED: {e}")
            test_results['get_session_replay'] = False
    else:
        print("\n4. Skipping get_session_replay (no session ID)")
        test_results['get_session_replay'] = 'skipped'
    
    # Test 5: Get session events (if we have a session)
    if session_id:
        try:
            print(f"\n5. Testing get_session_events with session {session_id}...")
            result = await client.get_session_events(session_id)
            events = result.get('data', [])
            print(f"   ✅ SUCCESS: Found {len(events)} events")
            test_results['get_session_events'] = True
        except Exception as e:
            if "404" in str(e):
                print(f"   ⚠️ EXPECTED FAIL: Events endpoint might not be available")
            else:
                print(f"   ❌ FAILED: {e}")
            test_results['get_session_events'] = False
    else:
        print("\n5. Skipping get_session_events (no session ID)")
        test_results['get_session_events'] = 'skipped'
    
    # Test 6: Get live sessions
    try:
        print("\n6. Testing get_live_sessions...")
        result = await client.get_live_sessions()
        sessions = result.get('data', {}).get('sessions', [])
        print(f"   ✅ SUCCESS: Found {len(sessions)} live sessions")
        test_results['get_live_sessions'] = True
    except Exception as e:
        if "404" in str(e):
            print(f"   ⚠️ EXPECTED FAIL: Live sessions endpoint might not be available")
        else:
            print(f"   ❌ FAILED: {e}")
        test_results['get_live_sessions'] = False
    
    # Test 7: Autocomplete
    try:
        print("\n7. Testing autocomplete...")
        result = await client.autocomplete("test")
        print(f"   ✅ SUCCESS: Got autocomplete data")
        test_results['autocomplete'] = True
    except Exception as e:
        if "404" in str(e):
            print(f"   ⚠️ EXPECTED FAIL: Autocomplete endpoint might not be available")
        else:
            print(f"   ❌ FAILED: {e}")
        test_results['autocomplete'] = False
    
    # Test 8: Error endpoints
    try:
        print("\n8. Testing search_errors...")
        result = await client.search_errors(limit=5)
        print(f"   ✅ SUCCESS: Got error data")
        test_results['search_errors'] = True
    except Exception as e:
        if "404" in str(e):
            print(f"   ⚠️ EXPECTED FAIL: Error search endpoint might not be available")
        else:
            print(f"   ❌ FAILED: {e}")
        test_results['search_errors'] = False
    
    # Test 9: Session notes (if we have a session)
    if session_id:
        try:
            print(f"\n9. Testing get_session_notes with session {session_id}...")
            result = await client.get_session_notes(session_id)
            notes = result.get('data', [])
            print(f"   ✅ SUCCESS: Found {len(notes)} notes")
            test_results['get_session_notes'] = True
        except Exception as e:
            if "404" in str(e):
                print(f"   ⚠️ EXPECTED FAIL: Notes endpoint might not be available")
            else:
                print(f"   ❌ FAILED: {e}")
            test_results['get_session_notes'] = False
    else:
        print("\n9. Skipping get_session_notes (no session ID)")
        test_results['get_session_notes'] = 'skipped'
    
    # Clean up
    await client.close()
    
    # Summary
    print("\n" + "=" * 60)
    print("API METHOD TEST SUMMARY")
    print("=" * 60)
    
    working_methods = []
    failing_methods = []
    skipped_methods = []
    
    for method, result in test_results.items():
        if result is True:
            working_methods.append(method)
            print(f"✅ {method}")
        elif result is False:
            failing_methods.append(method)
            print(f"❌ {method}")
        else:
            skipped_methods.append(method)
            print(f"⏭️ {method}")
    
    print(f"\nWorking: {len(working_methods)}")
    print(f"Failing: {len(failing_methods)}")
    print(f"Skipped: {len(skipped_methods)}")
    
    return test_results

if __name__ == "__main__":
    asyncio.run(test_api_methods())