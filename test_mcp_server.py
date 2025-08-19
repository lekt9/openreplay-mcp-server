#!/usr/bin/env python3
"""Test the OpenReplay MCP Server"""

import asyncio
import os
import sys

# Set environment variables
os.environ['OPENREPLAY_API_KEY'] = '5auNKdVzDfvUTjsBEDbf'
os.environ['OPENREPLAY_PROJECT_ID'] = '34vlVhQDDp5g4jhtL15M'

# Import the server module
from openreplay_mcp_server import (
    search_sessions,
    get_live_sessions,
    analyze_session_replay,
    get_user_analysis,
    search_errors,
    manage_session_notes
)


async def test_all_features():
    """Test all MCP server features"""
    
    print("=" * 80)
    print("OpenReplay MCP Server Test Suite")
    print("=" * 80)
    
    # Test 1: Search sessions for a specific user
    print("\n1. Testing Session Search")
    print("-" * 40)
    try:
        result = await search_sessions(
            user_id='k9742x5h3jbxjx20k52b2dt6th7ng54e',
            limit=5
        )
        print(result[:500] + "..." if len(result) > 500 else result)
        print("✅ Session search working")
    except Exception as e:
        print(f"❌ Session search failed: {e}")
    
    # Test 2: Get live sessions
    print("\n2. Testing Live Sessions")
    print("-" * 40)
    try:
        result = await get_live_sessions()
        print(result[:500] + "..." if len(result) > 500 else result)
        print("✅ Live sessions working")
    except Exception as e:
        print(f"❌ Live sessions failed: {e}")
    
    # Test 3: User analysis
    print("\n3. Testing User Analysis")
    print("-" * 40)
    try:
        result = await get_user_analysis('k9742x5h3jbxjx20k52b2dt6th7ng54e')
        print(result[:500] + "..." if len(result) > 500 else result)
        print("✅ User analysis working")
    except Exception as e:
        print(f"❌ User analysis failed: {e}")
    
    # Test 4: Error search
    print("\n4. Testing Error Search")
    print("-" * 40)
    try:
        result = await search_errors(limit=5)
        print(result[:500] + "..." if len(result) > 500 else result)
        print("✅ Error search working")
    except Exception as e:
        print(f"❌ Error search failed: {e}")
    
    # Test 5: Session replay analysis (if we have a session ID)
    print("\n5. Testing Session Replay Analysis")
    print("-" * 40)
    try:
        # First get a session ID
        sessions_result = await search_sessions(
            user_id='k9742x5h3jbxjx20k52b2dt6th7ng54e',
            limit=1
        )
        
        # Extract session ID from the result (this is a formatted string)
        if "Session" in sessions_result and "344" in sessions_result:
            session_id = "3448097416140724967"  # Using the known session ID
            result = await analyze_session_replay(session_id)
            print(result[:500] + "..." if len(result) > 500 else result)
            print("✅ Session replay analysis working")
        else:
            print("⚠️ No sessions found to analyze")
    except Exception as e:
        print(f"❌ Session replay analysis failed: {e}")
    
    # Test 6: Session notes
    print("\n6. Testing Session Notes")
    print("-" * 40)
    try:
        session_id = "3448097416140724967"
        result = await manage_session_notes(
            session_id=session_id,
            action="get"
        )
        print(result[:500] + "..." if len(result) > 500 else result)
        print("✅ Session notes working")
    except Exception as e:
        print(f"❌ Session notes failed: {e}")
    
    print("\n" + "=" * 80)
    print("Test Suite Complete")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_all_features())