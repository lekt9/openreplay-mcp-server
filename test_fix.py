#!/usr/bin/env python3
"""Test the MCP server fix for session analysis without user_id"""

import asyncio
import os

# Set environment variables
os.environ['OPENREPLAY_API_KEY'] = '5auNKdVzDfvUTjsBEDbf'
os.environ['OPENREPLAY_PROJECT_ID'] = '34vlVhQDDp5g4jhtL15M'

from openreplay_session_analyzer import openreplay_tools

async def test_fixed_methods():
    """Test the fixed methods that now work with just session_id"""
    
    session_id = "3448097416140724967"  # Known working session
    
    print("Testing Fixed MCP Methods")
    print("=" * 50)
    
    try:
        # Test analyze_user_journey with just session_id
        print("\n1. Testing analyze_user_journey (session_id only)")
        result = await openreplay_tools.analyze_user_journey(session_id)
        print("✅ SUCCESS")
        print(result[:200] + "..." if len(result) > 200 else result)
        
        # Test detect_problem_patterns with just session_id  
        print("\n2. Testing detect_problem_patterns (session_id only)")
        result = await openreplay_tools.detect_problem_patterns(session_id)
        print("✅ SUCCESS") 
        print(result[:200] + "..." if len(result) > 200 else result)
        
        # Test generate_session_summary with just session_id
        print("\n3. Testing generate_session_summary (session_id only)")
        result = await openreplay_tools.generate_session_summary(session_id)
        print("✅ SUCCESS")
        print(result[:200] + "..." if len(result) > 200 else result)
        
        print(f"\n{'=' * 50}")
        print("🎉 ALL FIXES WORKING! The MCP tools now work with just session_id")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await openreplay_tools.client.close()

if __name__ == "__main__":
    asyncio.run(test_fixed_methods())