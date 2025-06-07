"""
Standalone script to run the OpenReplay MCP Server using FastMCP
"""
import os
import sys
import asyncio
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables if not set
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# Import required modules after setting up path
from mcp.server.fastmcp import FastMCP
from openreplay_session_analyzer import OpenReplayConfig, OpenReplayClient, SessionAnalyzer

# Create FastMCP server
mcp = FastMCP("OpenReplay Session Analysis")

# Initialize OpenReplay components
config = OpenReplayConfig()
client = OpenReplayClient(config)
analyzer = SessionAnalyzer()

@mcp.tool()
async def search_sessions(
    limit: int = 50,
    start_date: str = None,
    end_date: str = None,
    user_id: str = None,
    has_errors: bool = None,
    min_duration: int = None
) -> str:
    """
    Search for OpenReplay sessions with various filters.
    
    Args:
        limit: Number of sessions to return (default: 50)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        user_id: Filter by specific user ID
        has_errors: Filter sessions with/without errors
        min_duration: Minimum session duration in seconds
    """
    try:
        result = await client.search_sessions(
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            has_errors=has_errors,
            min_duration=min_duration
        )
        
        sessions = result.get('sessions', [])
        summary = f"Found {len(sessions)} sessions matching criteria:\n\n"
        
        for session in sessions[:10]:  # Show first 10
            summary += f"• Session {session.get('id')}: {session.get('duration', 0)/1000:.1f}s"
            if session.get('user_id'):
                summary += f" (User: {session.get('user_id')})"
            if session.get('errors_count', 0) > 0:
                summary += f" ⚠️ {session.get('errors_count')} errors"
            summary += f" - {session.get('created_at', 'Unknown date')}\n"
        
        return summary
        
    except Exception as e:
        return f"Error searching sessions: {str(e)}"

@mcp.tool()
async def get_session_details(session_id: str) -> str:
    """
    Get detailed information about a specific session.
    
    Args:
        session_id: The ID of the session to analyze
    """
    try:
        session_data = await client.get_session_details(session_id)
        
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

async def main():
    """Main entry point for the MCP server"""
    print("🔥 OpenReplay Session Analysis MCP Server")
    print("=" * 50)
    print(f"API URL: {config.api_url}")
    print(f"Project ID: {config.project_id}")
    print(f"API Key configured: {'Yes' if config.api_key else 'No'}")
    print("=" * 50)
    
    if not config.api_key:
        print("⚠️  Warning: OPENREPLAY_API_KEY not set!")
        print("   Set your API key in environment variables or .env file")
    
    if not config.project_id:
        print("⚠️  Warning: OPENREPLAY_PROJECT_ID not set!")
        print("   Set your project ID in environment variables or .env file")
    
    print("\n🚀 Starting MCP server...")
    print("   Use with MCP-compatible clients like Claude Desktop")
    print("   Server will run on stdio transport")
    print("\n" + "=" * 50)
    
    await mcp.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)
