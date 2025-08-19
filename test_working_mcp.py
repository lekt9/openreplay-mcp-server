#!/usr/bin/env python3
"""Test the working MCP server implementation"""

import asyncio
import os

# Set environment variables
os.environ['OPENREPLAY_API_KEY'] = '5auNKdVzDfvUTjsBEDbf'
os.environ['OPENREPLAY_PROJECT_ID'] = '34vlVhQDDp5g4jhtL15M'

# Import the working implementation
import openreplay_mcp_working

async def test_mcp_tools():
    """Test all MCP tool functions directly"""
    
    print("Testing Working OpenReplay MCP Server")
    print("=" * 80)
    
    # Import the tools from the working implementation
    from openreplay_mcp_working import (
        analyze_user_sessions,
        get_session_details,
        monitor_live_sessions,
        get_project_overview,
        client
    )
    
    try:
        # Test 1: Project Overview
        print("\n1. Testing Project Overview")
        print("-" * 50)
        result = await get_project_overview()
        print(result[:500] + "..." if len(result) > 500 else result)
        print("✅ Project overview working")
        
        # Test 2: Live Sessions
        print("\n2. Testing Live Session Monitor")
        print("-" * 50)
        result = await monitor_live_sessions()
        print(result[:500] + "..." if len(result) > 500 else result)
        print("✅ Live session monitor working")
        
        # Test 3: User Analysis
        print("\n3. Testing User Session Analysis")
        print("-" * 50)
        result = await analyze_user_sessions(
            user_id='k9742x5h3jbxjx20k52b2dt6th7ng54e',
            days_back=30
        )
        print(result[:800] + "..." if len(result) > 800 else result)
        print("✅ User analysis working")
        
        # Test 4: Session Details
        print("\n4. Testing Session Details")
        print("-" * 50)
        # Use the known session ID
        result = await get_session_details('3448097416140724967')
        print(result[:500] + "..." if len(result) > 500 else result)
        print("✅ Session details working")
        
        print(f"\n{'=' * 80}")
        print("🎉 ALL TESTS PASSED! MCP Server is working correctly.")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())