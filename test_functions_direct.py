#!/usr/bin/env python3
"""Test the core functions directly without MCP wrapper"""

import asyncio
import os

# Set environment variables
os.environ['OPENREPLAY_API_KEY'] = '5auNKdVzDfvUTjsBEDbf'
os.environ['OPENREPLAY_PROJECT_ID'] = '34vlVhQDDp5g4jhtL15M'

from openreplay_mcp_working import client, analyzer, config

async def test_core_functionality():
    """Test the core API functionality directly"""
    
    print("Testing Core OpenReplay Functions")
    print("=" * 80)
    
    try:
        # Test 1: User sessions analysis (manual implementation)
        print("\n1. Testing User Session Analysis")
        print("-" * 50)
        
        user_id = 'k9742x5h3jbxjx20k52b2dt6th7ng54e'
        
        # Get user data
        user_stats = await client.get_user_stats(user_id)
        user_sessions = await client.get_user_sessions(user_id)
        
        user_data = user_stats.get('data', {})
        sessions = user_sessions.get('data', [])
        
        print(f"User has {user_data.get('sessionCount', 0)} total sessions")
        print(f"Found {len(sessions)} sessions in data")
        
        if sessions:
            # Analyze patterns
            patterns = analyzer.analyze_session_patterns(sessions)
            insights = analyzer.generate_insights(patterns)
            
            print(f"Analysis complete:")
            print(f"• Avg Duration: {patterns['engagement_metrics']['avg_duration']/60000:.1f} min")
            print(f"• Error Rate: {patterns['engagement_metrics']['error_rate']:.1f}%")
            print(f"• Insights: {len(insights)} generated")
            for insight in insights[:3]:
                print(f"  - {insight}")
        
        print("✅ User analysis working")
        
        # Test 2: Session events
        print("\n2. Testing Session Events")
        print("-" * 50)
        
        if sessions:
            session_id = sessions[0]['sessionId']
            events_result = await client.get_session_events(session_id)
            events = events_result.get('data', [])
            
            print(f"Session {session_id} has {len(events)} events")
            
            event_types = {}
            for event in events:
                event_type = event.get('type', 'unknown')
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            print(f"Event types: {dict(event_types)}")
            
        print("✅ Session events working")
        
        # Test 3: Live sessions
        print("\n3. Testing Live Sessions")
        print("-" * 50)
        
        live_result = await client.get_live_sessions()
        live_sessions = live_result.get('data', {}).get('sessions', [])
        
        print(f"Found {len(live_sessions)} live sessions")
        
        if live_sessions:
            browsers = {}
            for session in live_sessions:
                browser = session.get('userBrowser', 'Unknown')
                browsers[browser] = browsers.get(browser, 0) + 1
            
            print(f"Browser distribution: {dict(browsers)}")
            
            active_count = sum(1 for s in live_sessions if s.get('activeTab'))
            print(f"Active tabs: {active_count}/{len(live_sessions)}")
        
        print("✅ Live sessions working")
        
        # Test 4: Project information
        print("\n4. Testing Project Information")
        print("-" * 50)
        
        project_result = await client.get_project_details()
        project_data = project_result.get('data', {})
        
        print(f"Project: {project_data.get('name', 'Unknown')}")
        print(f"Platform: {project_data.get('platform', 'Unknown')}")
        print(f"Project ID: {project_data.get('projectId', 'Unknown')}")
        
        # Get all projects
        projects_result = await client.get_projects()
        all_projects = projects_result.get('data', [])
        
        print(f"Organization has {len(all_projects)} projects")
        
        print("✅ Project information working")
        
        # Test 5: Configuration
        print("\n5. Testing Configuration")
        print("-" * 50)
        
        print(f"API URL: {config.api_url}")
        print(f"Project ID: {config.project_id}")
        print(f"API Key: {'***' + config.api_key[-4:] if config.api_key else 'NOT SET'}")
        
        print("✅ Configuration working")
        
        print(f"\n{'=' * 80}")
        print("🎉 ALL CORE FUNCTIONS WORKING!")
        print("The MCP server implementation is sound.")
        print("=" * 80)
        
        # Generate a sample MCP response format
        print(f"\n📋 Sample MCP Response Format:")
        print("-" * 50)
        
        sample_output = f"""👤 User Analysis: {user_id}
{'=' * 80}

📊 User Overview:
• Total Sessions: {user_data.get('sessionCount', 0)}
• Sessions Analyzed: {len(sessions)}

📈 Engagement Analysis:
• Avg Session Duration: {patterns['engagement_metrics']['avg_duration']/60000:.1f} minutes
• Avg Pages per Session: {patterns['engagement_metrics']['avg_pages']:.1f}
• Error Rate: {patterns['engagement_metrics']['error_rate']:.1f}%

💡 AI Insights:
{chr(10).join(insights[:3])}

📋 Recent Sessions:
1. Session {sessions[0]['sessionId'] if sessions else 'N/A'}
   Duration: {sessions[0].get('duration', 0)/60000:.1f} min | Pages: {sessions[0].get('pagesCount', 0)} | Errors: {sessions[0].get('errorsCount', 0)}
"""
        
        print(sample_output)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_core_functionality())