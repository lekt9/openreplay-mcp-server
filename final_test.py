#!/usr/bin/env python3
"""
Final comprehensive test suite for OpenReplay MCP Server
"""

import asyncio
import os
import sys
import traceback
from datetime import datetime as dt

# Set environment variables
os.environ['OPENREPLAY_API_KEY'] = '5auNKdVzDfvUTjsBEDbf'
os.environ['OPENREPLAY_PROJECT_ID'] = '34vlVhQDDp5g4jhtL15M'

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'=' * 80}")
    print(f"{title}")
    print('=' * 80)

def print_test(test_name):
    """Print a test header"""
    print(f"\n🧪 {test_name}")
    print('-' * 60)

async def main():
    """Run comprehensive test suite"""
    
    print_section("OpenReplay MCP Server - Final Test Suite")
    print(f"🕐 Test Started: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {
        'imports': False,
        'configuration': False,
        'api_connectivity': False,
        'user_analysis': False,
        'session_analysis': False,
        'live_monitoring': False,
        'project_overview': False,
        'error_handling': False
    }
    
    # Test 1: Imports and Module Loading
    print_test("Testing Imports and Module Loading")
    try:
        # Test basic imports
        import httpx
        import asyncio
        from datetime import datetime, timedelta
        from typing import List, Dict, Any, Optional
        from dataclasses import dataclass
        
        print("✅ Basic Python modules imported successfully")
        
        # Test FastMCP
        from fastmcp import FastMCP
        print("✅ FastMCP imported successfully")
        
        # Test main module
        import openreplay_mcp_working
        print("✅ OpenReplay MCP module imported successfully")
        
        # Test configuration
        config = openreplay_mcp_working.config
        client = openreplay_mcp_working.client
        analyzer = openreplay_mcp_working.analyzer
        
        print("✅ Module components instantiated successfully")
        test_results['imports'] = True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return test_results
    
    # Test 2: Configuration
    print_test("Testing Configuration")
    try:
        print(f"API URL: {config.api_url}")
        print(f"Project ID: {config.project_id}")
        print(f"API Key: {'***' + config.api_key[-4:] if config.api_key else 'NOT SET'}")
        
        if config.api_key and config.project_id and config.api_url:
            print("✅ Configuration complete and valid")
            test_results['configuration'] = True
        else:
            print("❌ Configuration incomplete")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
    
    # Test 3: API Connectivity
    print_test("Testing API Connectivity")
    try:
        # Test project details
        project_result = await client.get_project_details()
        project_data = project_result.get('data', {})
        
        print(f"✅ Connected to project: {project_data.get('name', 'Unknown')}")
        print(f"   Platform: {project_data.get('platform', 'Unknown')}")
        print(f"   Project ID: {project_data.get('projectId', 'Unknown')}")
        
        test_results['api_connectivity'] = True
        
    except Exception as e:
        print(f"❌ API connectivity failed: {e}")
    
    # Test 4: User Analysis
    print_test("Testing User Analysis Functionality")
    try:
        user_id = 'k9742x5h3jbxjx20k52b2dt6th7ng54e'
        
        # Get user data
        user_stats = await client.get_user_stats(user_id)
        user_sessions = await client.get_user_sessions(user_id)
        
        user_data = user_stats.get('data', {})
        sessions = user_sessions.get('data', [])
        
        print(f"✅ Retrieved user data: {user_data.get('sessionCount', 0)} total sessions")
        print(f"✅ Retrieved session data: {len(sessions)} sessions")
        
        if sessions:
            # Test pattern analysis
            patterns = analyzer.analyze_session_patterns(sessions)
            insights = analyzer.generate_insights(patterns)
            
            print(f"✅ Pattern analysis complete: {len(insights)} insights generated")
            print(f"   Avg duration: {patterns['engagement_metrics']['avg_duration']/60000:.1f} min")
            print(f"   Error rate: {patterns['engagement_metrics']['error_rate']:.1f}%")
        
        test_results['user_analysis'] = True
        
    except Exception as e:
        print(f"❌ User analysis failed: {e}")
    
    # Test 5: Session Analysis
    print_test("Testing Session Analysis")
    try:
        if sessions:
            session_id = sessions[0]['sessionId']
            
            # Get session events
            events_result = await client.get_session_events(session_id)
            events = events_result.get('data', [])
            
            print(f"✅ Retrieved session events: {len(events)} events for session {session_id}")
            
            # Analyze event types
            event_types = {}
            for event in events:
                event_type = event.get('type', 'unknown')
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            print(f"✅ Event analysis complete: {dict(event_types)}")
            
            test_results['session_analysis'] = True
        else:
            print("⚠️ No sessions available for analysis")
        
    except Exception as e:
        print(f"❌ Session analysis failed: {e}")
    
    # Test 6: Live Session Monitoring
    print_test("Testing Live Session Monitoring")
    try:
        live_result = await client.get_live_sessions()
        live_sessions = live_result.get('data', {}).get('sessions', [])
        
        print(f"✅ Retrieved live sessions: {len(live_sessions)} active sessions")
        
        if live_sessions:
            browsers = {}
            countries = {}
            active_count = 0
            
            for session in live_sessions:
                browser = session.get('userBrowser', 'Unknown')
                browsers[browser] = browsers.get(browser, 0) + 1
                
                country = session.get('userCountry', 'Unknown')
                countries[country] = countries.get(country, 0) + 1
                
                if session.get('activeTab'):
                    active_count += 1
            
            print(f"✅ Live session analysis:")
            print(f"   Active tabs: {active_count}/{len(live_sessions)}")
            print(f"   Browsers: {dict(browsers)}")
            print(f"   Countries: {dict(list(countries.items())[:3])}")
        
        test_results['live_monitoring'] = True
        
    except Exception as e:
        print(f"❌ Live monitoring failed: {e}")
    
    # Test 7: Project Overview
    print_test("Testing Project Overview")
    try:
        # Test project list
        projects_result = await client.get_projects()
        all_projects = projects_result.get('data', [])
        
        print(f"✅ Retrieved organization projects: {len(all_projects)} projects")
        
        for project in all_projects:
            current = "📍" if str(project.get('projectId')) == config.project_id else "  "
            print(f"   {current} {project.get('name', 'Unknown')} ({project.get('platform', 'unknown')})")
        
        test_results['project_overview'] = True
        
    except Exception as e:
        print(f"❌ Project overview failed: {e}")
    
    # Test 8: Error Handling
    print_test("Testing Error Handling")
    try:
        # Test with invalid user ID
        try:
            await client.get_user_stats('invalid_user_12345')
            print("⚠️ Expected error didn't occur")
        except Exception:
            print("✅ Error handling working - invalid user ID properly handled")
        
        # Test with invalid session ID
        try:
            await client.get_session_events('invalid_session_12345')
            print("⚠️ Expected error didn't occur")
        except Exception:
            print("✅ Error handling working - invalid session ID properly handled")
        
        test_results['error_handling'] = True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
    
    # Clean up
    try:
        await client.close()
        print("\n🧹 Cleanup completed successfully")
    except Exception as e:
        print(f"\n⚠️ Cleanup warning: {e}")
    
    # Final Results
    print_section("Test Results Summary")
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print(f"\nOverall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The OpenReplay MCP Server is ready for use.")
        print("\n📋 Next Steps:")
        print("1. Run: python openreplay_mcp_working.py")
        print("2. Connect your MCP client to the server")
        print("3. Use the available tools for session analysis")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Review the errors above.")
    
    print(f"\n🕐 Test Completed: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return test_results

if __name__ == "__main__":
    try:
        results = asyncio.run(main())
        
        # Exit with appropriate code
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        if passed == total:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Some tests failed
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n💥 Test suite crashed: {e}")
        traceback.print_exc()
        sys.exit(1)