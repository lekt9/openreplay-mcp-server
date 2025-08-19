"""
Standalone script to run the OpenReplay MCP Server using FastMCP
"""
import os
import sys
import asyncio
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import required modules
from fastmcp import FastMCP
from openreplay_session_analyzer import OpenReplayConfig, OpenReplayClient, SessionAnalyzer

# Create FastMCP server
mcp = FastMCP("OpenReplay Session Analysis")

# Initialize OpenReplay components
config = OpenReplayConfig()
client = OpenReplayClient(config)
analyzer = SessionAnalyzer()

@mcp.tool()
async def list_projects() -> str:
    """
    List all available projects in your OpenReplay account
    """
    try:
        result = await client.get_all_projects()
        projects = result.get('data', [])
        
        if not projects:
            return "No projects found. Make sure your API key has the correct permissions."
        
        summary = f"Found {len(projects)} project(s):\n\n"
        for project in projects:
            summary += f"• Project: {project.get('name', 'Unknown')}\n"
            summary += f"  Key: {project.get('projectKey', 'N/A')}\n\n"
        
        return summary
    except Exception as e:
        return f"Error listing projects: {str(e)}"

@mcp.tool()
async def get_user_info(user_id: str) -> str:
    """
    Get statistics and information about a specific user
    
    Args:
        user_id: The user ID to get information for
    """
    try:
        result = await client.get_user_stats(user_id)
        data = result.get('data', {})
        
        info = f"User Information for {user_id}:\n\n"
        info += f"• Session Count: {data.get('sessionCount', 0)}\n"
        
        first_seen = data.get('firstSeen')
        if first_seen:
            from datetime import datetime
            dt = datetime.fromtimestamp(first_seen / 1000)
            info += f"• First Seen: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        last_seen = data.get('lastSeen')
        if last_seen:
            from datetime import datetime
            dt = datetime.fromtimestamp(last_seen / 1000)
            info += f"• Last Seen: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return info
    except Exception as e:
        return f"Error getting user info: {str(e)}"

@mcp.tool()
async def get_api_help() -> str:
    """
    Get help and instructions for using the OpenReplay API
    """
    return """
OpenReplay API Usage Guide:

The OpenReplay API requires a user ID to fetch sessions. Here's how to use it:

1. **Required Configuration** (.env file):
   - OPENREPLAY_API_URL: Your OpenReplay instance URL (e.g., https://app.openreplay.com)
   - OPENREPLAY_API_KEY: Your Organization API key (from Preferences > Account)
   - OPENREPLAY_PROJECT_KEY: Your project key (from Preferences > Projects)

2. **Finding User IDs**:
   - Check your OpenReplay dashboard for user IDs
   - Look for tracker.setUserID() calls in your application
   - Common formats: email addresses, application user IDs, or anonymous IDs

3. **Available Tools**:
   - search_sessions(user_id="..."): Get sessions for a specific user
   - get_session_details(session_id="...", user_id="..."): Get session details
   - get_session_events(session_id="..."): Get events from a session
   - analyze_user_journey(session_id="..."): Analyze user navigation
   - detect_problem_patterns(session_id="..."): Find UX issues

Example usage:
1. search_sessions(user_id="user@example.com")
2. Use a session ID from the results
3. get_session_details(session_id="123456", user_id="user@example.com")
"""

@mcp.tool()
async def search_sessions(
    user_id: str = None,
    limit: int = 10,
    page: int = 1
) -> str:
    """
    Search for OpenReplay sessions.
    
    Args:
        user_id: Optional user ID to filter sessions
        limit: Number of sessions to return (default: 10)
        page: Page number for pagination (default: 1)
    """
    try:
        if not user_id:
            return "Error: user_id is required. Use the value from tracker.setUserID() in your application."
            
        result = await client.get_user_sessions(user_id)
        
        # Handle the official API response format
        sessions = result.get('data', [])
            
        summary = f"Found {len(sessions)} sessions for user {user_id}:\n\n"
        
        for session in sessions[:10]:  # Show first 10
            session_id = session.get('sessionId', session.get('id', 'Unknown'))
            duration = session.get('duration', 0)
            duration_sec = duration / 1000 if duration > 0 else 0
            
            summary += f"• Session {session_id}: {duration_sec:.1f}s"
            
            # Add timestamp info
            start_ts = session.get('startTs', session.get('start_ts'))
            if start_ts:
                summary += f" - {start_ts}"
                
            summary += "\n"
        
        return summary
        
    except Exception as e:
        return f"Error searching sessions: {str(e)}"

@mcp.tool()
async def get_session_details(session_id: str, user_id: str) -> str:
    """
    Get detailed information about a specific session.
    
    Args:
        session_id: The ID of the session to analyze
        user_id: The user ID associated with the session
    """
    try:
        session_data = await client.get_session_details(session_id, user_id)
        
        details = f"Session Details for {session_id}:\n"
        details += f"Duration: {session_data.get('duration', 0)/1000:.1f} seconds\n"
        details += f"User ID: {session_data.get('user_id', 'Anonymous')}\n"
        details += f"Pages Visited: {session_data.get('pages_count', 0)}\n"
        details += f"Events: {session_data.get('events_count', 0)}\n"
        details += f"Errors: {session_data.get('errors_count', 0)}\n"
        details += f"Created: {session_data.get('created_at', 'Unknown')}\n"
        details += f"User Agent: {session_data.get('user_agent', 'Unknown')}\n"
        details += f"Location: {session_data.get('country', 'Unknown')}\n"
        
        if session_data.get('replay_url'):
            details += f"\n🎥 Replay URL: {session_data['replay_url']}"
        
        return details
        
    except Exception as e:
        return f"Error getting session details: {str(e)}"

@mcp.tool()
async def analyze_user_journey(session_id: str) -> str:
    """
    Analyze user journey and navigation patterns for a session.
    
    Args:
        session_id: The ID of the session to analyze
    """
    try:
        session_data = await client.get_session_details(session_id)
        events_data = await client.get_session_events(session_id)
        
        # Combine session and events data
        full_session_data = {**session_data, 'events': events_data.get('events', [])}
        journey = analyzer.analyze_user_journey(full_session_data)
        
        analysis = f"User Journey Analysis for Session {session_id}:\n\n"
        analysis += f"📊 Overview:\n"
        analysis += f"• Pages visited: {journey['pages_visited']}\n"
        analysis += f"• Total actions: {journey['total_actions']}\n"
        analysis += f"• Session duration: {journey['session_duration']/1000:.1f}s\n"
        analysis += f"• Bounce rate: {'Yes' if journey['bounce_rate'] else 'No'}\n\n"
        
        if journey['page_flow']:
            analysis += f"🗺️ Page Flow:\n"
            for i, page in enumerate(journey['page_flow'][:5]):  # Show first 5 pages
                analysis += f"{i+1}. {page['url']} ({page['duration']/1000:.1f}s)\n"
        
        return analysis
        
    except Exception as e:
        return f"Error analyzing user journey: {str(e)}"

@mcp.tool()
async def detect_problem_patterns(session_id: str) -> str:
    """
    Detect rage clicks, dead clicks, form abandonment and other issues.
    
    Args:
        session_id: The ID of the session to analyze
    """
    try:
        session_data = await client.get_session_details(session_id)
        events_data = await client.get_session_events(session_id)
        
        full_session_data = {**session_data, 'events': events_data.get('events', [])}
        problems = analyzer.detect_problem_patterns(full_session_data)
        
        report = f"Problem Pattern Analysis for Session {session_id}:\n\n"
        
        if problems['rage_clicks']:
            report += f"😤 Rage Clicks Detected: {len(problems['rage_clicks'])}\n"
            for rage in problems['rage_clicks'][:3]:
                report += f"  • {rage['click_count']} clicks on {rage['element']}\n"
        
        if problems['form_abandonment']:
            report += f"\n📝 Form Abandonment:\n"
            for field in problems['form_abandonment'][:5]:
                report += f"  • Abandoned field: {field}\n"
        
        if problems['error_occurrences']:
            report += f"\n🐛 Errors: {len(problems['error_occurrences'])}\n"
            for error in problems['error_occurrences'][:3]:
                report += f"  • {error.get('message', 'Unknown error')}\n"
        
        if not any(problems.values()):
            report += "✅ No significant problems detected in this session."
        
        return report
        
    except Exception as e:
        return f"Error detecting problem patterns: {str(e)}"

@mcp.tool()
async def generate_session_summary(session_id: str) -> str:
    """
    Generate AI-powered summary and insights for a session.
    
    Args:
        session_id: The ID of the session to summarize
    """
    try:
        session_data = await client.get_session_details(session_id)
        events_data = await client.get_session_events(session_id)
        
        full_session_data = {**session_data, 'events': events_data.get('events', [])}
        journey = analyzer.analyze_user_journey(full_session_data)
        problems = analyzer.detect_problem_patterns(full_session_data)
        insights = analyzer.generate_session_insights(full_session_data, problems, journey)
        
        summary = f"Session Summary for {session_id}:\n\n"
        summary += f"📈 Key Metrics:\n"
        summary += f"• Duration: {session_data.get('duration', 0)/1000:.1f} seconds\n"
        summary += f"• Pages: {journey['pages_visited']}\n"
        summary += f"• Actions: {journey['total_actions']}\n"
        summary += f"• User: {session_data.get('user_id', 'Anonymous')}\n\n"
        
        summary += f"🔍 AI Insights:\n{insights}\n\n"
        
        if session_data.get('replay_url'):
            summary += f"🎥 Watch replay: {session_data['replay_url']}"
        
        return summary
        
    except Exception as e:
        return f"Error generating session summary: {str(e)}"

@mcp.tool()
async def find_similar_sessions(reference_session_id: str, similarity_criteria: str = "errors") -> str:
    """
    Find sessions with similar patterns or issues.
    
    Args:
        reference_session_id: Reference session to find similar ones
        similarity_criteria: Criteria for similarity (errors, journey, duration, user_behavior)
    """
    try:
        # Get reference session
        ref_session = await client.get_session_details(reference_session_id)
        
        # Search for similar sessions based on criteria
        search_params = {"limit": 20}
        if similarity_criteria == "errors" and ref_session.get('errors_count', 0) > 0:
            search_params["has_errors"] = True
        elif similarity_criteria == "duration":
            duration = ref_session.get('duration', 0)
            search_params["min_duration"] = max(0, duration // 1000 - 30)  # Within 30 seconds
        
        similar_sessions = await client.search_sessions(**search_params)
        sessions = similar_sessions.get('sessions', [])
        
        result = f"Similar Sessions to {reference_session_id} (by {similarity_criteria}):\n\n"
        for session in sessions[:10]:
            if session.get('id') != reference_session_id:  # Exclude reference session
                result += f"• {session.get('id')}: {session.get('duration', 0)/1000:.1f}s"
                if session.get('errors_count', 0) > 0:
                    result += f" ({session['errors_count']} errors)"
                result += f" - {session.get('created_at', 'Unknown')}\n"
        
        return result
        
    except Exception as e:
        return f"Error finding similar sessions: {str(e)}"

@mcp.tool()
async def get_user_session_history(user_id: str, limit: int = 20) -> str:
    """
    Get all sessions for a specific user to analyze behavior patterns.
    
    Args:
        user_id: The ID of the user to analyze
        limit: Number of sessions to return (default: 20)
    """
    try:
        user_sessions = await client.get_user_sessions(user_id, limit)
        sessions = user_sessions.get('sessions', [])
        
        history = f"Session History for User {user_id}:\n\n"
        history += f"Total sessions found: {len(sessions)}\n\n"
        
        for i, session in enumerate(sessions, 1):
            history += f"{i}. Session {session.get('id')}\n"
            history += f"   Duration: {session.get('duration', 0)/1000:.1f}s\n"
            history += f"   Pages: {session.get('pages_count', 0)}\n"
            history += f"   Date: {session.get('created_at', 'Unknown')}\n"
            if session.get('errors_count', 0) > 0:
                history += f"   ⚠️ Errors: {session['errors_count']}\n"
            history += "\n"
        
        return history
        
    except Exception as e:
        return f"Error getting user session history: {str(e)}"

def main():
    """Main entry point for the MCP server"""
    print("🔥 OpenReplay Session Analysis MCP Server")
    print("=" * 50)
    print(f"API URL: {config.api_url}")
    print(f"Project Key: {config.project_key}")
    print(f"API Key configured: {'Yes' if config.api_key else 'No'}")
    print("=" * 50)
    
    if not config.api_key:
        print("⚠️  Warning: OPENREPLAY_API_KEY not set!")
        print("   Set your Organization API key in environment variables or .env file")
    
    if not config.project_key:
        print("⚠️  Warning: OPENREPLAY_PROJECT_KEY not set!")
        print("   Set your project key in environment variables or .env file")
    
    print("\n🚀 Starting MCP server...")
    print("   Use with MCP-compatible clients like Claude Desktop")
    print("   Server will run on stdio transport")
    print("\n" + "=" * 50)
    
    # Run the server synchronously
    mcp.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
