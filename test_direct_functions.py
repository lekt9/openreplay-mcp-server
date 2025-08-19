#!/usr/bin/env python3
"""Direct test of OpenReplay functions"""

import asyncio
import os

# Set environment variables
os.environ['OPENREPLAY_API_KEY'] = '5auNKdVzDfvUTjsBEDbf'
os.environ['OPENREPLAY_PROJECT_ID'] = '34vlVhQDDp5g4jhtL15M'

from openreplay_mcp_server import client, analyzer


async def test_direct():
    """Test direct API calls"""
    
    print("Testing Direct API Calls")
    print("=" * 60)
    
    try:
        # Test search sessions
        print("\n1. Search Sessions")
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
        print(f"Found {len(sessions)} sessions")
        
        if sessions:
            session = sessions[0]
            print(f"First session: {session['sessionId']}")
            print(f"Duration: {session.get('duration', 0)/60000:.1f} min")
            print(f"Pages: {session.get('pagesCount', 0)}")
            print(f"Errors: {session.get('errorsCount', 0)}")
            
            # Analyze patterns
            patterns = analyzer.analyze_session_patterns(sessions)
            print(f"\nSession Analysis:")
            print(f"Avg Duration: {patterns['engagement_metrics']['avg_duration']/60000:.1f} min")
            print(f"Error Rate: {patterns['issue_analysis']['error_rate']:.1f}%")
        
        # Test user stats
        print("\n2. User Stats")
        result = await client.get_user_stats("k9742x5h3jbxjx20k52b2dt6th7ng54e")
        user_data = result.get('data', {})
        print(f"Session Count: {user_data.get('sessionCount', 0)}")
        
        # Test live sessions
        print("\n3. Live Sessions")
        result = await client.get_live_sessions()
        live_sessions = result.get('data', {}).get('sessions', [])
        print(f"Active Sessions: {len(live_sessions)}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_direct())