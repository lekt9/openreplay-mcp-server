"""
OpenReplay Session Analysis MCP Server
Django-based MCP server for analyzing OpenReplay session data
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import httpx
from django.conf import settings
from django.core.management.base import BaseCommand
from django_mcp_server import MCPServer
from mcp.types import (
    Tool, 
    TextContent, 
    Resource, 
    Prompt,
    PromptMessage,
    GetPromptResult
)

# Django settings configuration
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='openreplay-mcp-server-key',
        INSTALLED_APPS=[
            'django_mcp_server',
        ],
        USE_TZ=True,
    )

@dataclass
class OpenReplayConfig:
    """OpenReplay API configuration"""
    api_url: str = os.getenv('OPENREPLAY_API_URL', 'https://api.openreplay.com')
    api_key: str = os.getenv('OPENREPLAY_API_KEY', '')
    project_id: str = os.getenv('OPENREPLAY_PROJECT_ID', '')

class OpenReplayClient:
    """Client for OpenReplay API interactions"""
    
    def __init__(self, config: OpenReplayConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            headers={
                'Authorization': f'Bearer {config.api_key}',
                'Content-Type': 'application/json'
            },
            timeout=30.0
        )
    
    async def search_sessions(
        self,
        limit: int = 50,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user_id: Optional[str] = None,
        has_errors: Optional[bool] = None,
        min_duration: Optional[int] = None,
        filters: Optional[Dict] = None
    ) -> Dict:
        """Search for sessions with various filters"""
        params = {
            'limit': limit,
            'projectId': self.config.project_id
        }
        
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if user_id:
            params['userId'] = user_id
        if has_errors is not None:
            params['hasErrors'] = has_errors
        if min_duration:
            params['minDuration'] = min_duration
        if filters:
            params.update(filters)
        
        response = await self.client.get(
            f"{self.config.api_url}/v1/sessions",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def get_session_details(self, session_id: str) -> Dict:
        """Get detailed information about a specific session"""
        response = await self.client.get(
            f"{self.config.api_url}/v1/sessions/{session_id}"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_session_events(self, session_id: str) -> Dict:
        """Get events for a specific session"""
        response = await self.client.get(
            f"{self.config.api_url}/v1/sessions/{session_id}/events"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_session_errors(self, session_id: str) -> Dict:
        """Get errors for a specific session"""
        response = await self.client.get(
            f"{self.config.api_url}/v1/sessions/{session_id}/errors"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_user_sessions(self, user_id: str, limit: int = 20) -> Dict:
        """Get all sessions for a specific user"""
        return await self.search_sessions(
            limit=limit,
            user_id=user_id
        )

class SessionAnalyzer:
    """Analyzer for session data and user behavior patterns"""
    
    @staticmethod
    def analyze_user_journey(session_data: Dict) -> Dict:
        """Analyze user journey through pages and actions"""
        events = session_data.get('events', [])
        pages = []
        actions = []
        
        for event in events:
            if event.get('type') == 'page_view':
                pages.append({
                    'url': event.get('url'),
                    'timestamp': event.get('timestamp'),
                    'duration': event.get('duration', 0)
                })
            elif event.get('type') in ['click', 'input', 'scroll']:
                actions.append({
                    'type': event.get('type'),
                    'element': event.get('element'),
                    'timestamp': event.get('timestamp')
                })
        
        return {
            'pages_visited': len(pages),
            'page_flow': pages,
            'total_actions': len(actions),
            'action_breakdown': actions,
            'session_duration': session_data.get('duration', 0),
            'bounce_rate': 1 if len(pages) == 1 else 0
        }
    
    @staticmethod
    def detect_problem_patterns(session_data: Dict) -> Dict:
        """Detect rage clicks, dead clicks, and form abandonment"""
        events = session_data.get('events', [])
        problems = {
            'rage_clicks': [],
            'dead_clicks': [],
            'form_abandonment': [],
            'error_occurrences': []
        }
        
        # Detect rage clicks (multiple clicks in short time)
        click_events = [e for e in events if e.get('type') == 'click']
        for i, click in enumerate(click_events[:-2]):
            next_clicks = click_events[i+1:i+4]
            if len(next_clicks) >= 2:
                time_diff = next_clicks[-1].get('timestamp', 0) - click.get('timestamp', 0)
                if time_diff < 3000:  # 3 seconds
                    problems['rage_clicks'].append({
                        'element': click.get('element'),
                        'timestamp': click.get('timestamp'),
                        'click_count': len(next_clicks) + 1
                    })
        
        # Detect form abandonment
        form_events = [e for e in events if e.get('type') in ['input', 'focus', 'blur']]
        form_fields = {}
        for event in form_events:
            field = event.get('element')
            if field:
                if field not in form_fields:
                    form_fields[field] = {'interactions': 0, 'completed': False}
                form_fields[field]['interactions'] += 1
        
        # Check for abandoned forms (interactions but no submission)
        submit_events = [e for e in events if e.get('type') == 'submit']
        if form_fields and not submit_events:
            problems['form_abandonment'] = list(form_fields.keys())
        
        # Extract errors
        problems['error_occurrences'] = [
            e for e in events if e.get('type') == 'error'
        ]
        
        return problems
    
    @staticmethod
    def generate_session_insights(session_data: Dict, problems: Dict, journey: Dict) -> str:
        """Generate AI-powered insights about the session"""
        insights = []
        
        # Duration insights
        duration = session_data.get('duration', 0) / 1000  # Convert to seconds
        if duration < 10:
            insights.append("⚠️ Very short session - user may have encountered immediate issues")
        elif duration > 300:
            insights.append("✅ Long engagement session - user was actively exploring")
        
        # Journey insights
        if journey['bounce_rate'] == 1:
            insights.append("🔍 Single page session - check landing page effectiveness")
        
        if journey['pages_visited'] > 10:
            insights.append("🗺️ Extensive navigation - user was searching for specific content")
        
        # Problem insights
        if problems['rage_clicks']:
            insights.append(f"😤 {len(problems['rage_clicks'])} rage click incidents detected - UI elements may be unresponsive")
        
        if problems['form_abandonment']:
            insights.append(f"📝 Form abandonment detected on {len(problems['form_abandonment'])} fields")
        
        if problems['error_occurrences']:
            insights.append(f"🐛 {len(problems['error_occurrences'])} errors occurred during session")
        
        # Performance insights
        if 'performance' in session_data:
            perf = session_data['performance']
            if perf.get('load_time', 0) > 3000:
                insights.append("🐌 Slow page load times detected - may impact user experience")
        
        return "\n".join(insights) if insights else "✅ Session appears normal with no major issues detected"

# Initialize OpenReplay client
config = OpenReplayConfig()
openreplay_client = OpenReplayClient(config)
analyzer = SessionAnalyzer()

# Create MCP Server
server = MCPServer("openreplay-session-analysis")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available tools for session analysis"""
    return [
        Tool(
            name="search_sessions",
            description="Search for OpenReplay sessions with various filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 50, "description": "Number of sessions to return"},
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "user_id": {"type": "string", "description": "Filter by specific user ID"},
                    "has_errors": {"type": "boolean", "description": "Filter sessions with/without errors"},
                    "min_duration": {"type": "integer", "description": "Minimum session duration in seconds"}
                }
            }
        ),
        Tool(
            name="get_session_details",
            description="Get detailed information about a specific session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Session ID to analyze"}
                },
                "required": ["session_id"]
            }
        ),
        Tool(
            name="analyze_user_journey",
            description="Analyze user journey and navigation patterns for a session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Session ID to analyze"}
                },
                "required": ["session_id"]
            }
        ),
        Tool(
            name="detect_problem_patterns",
            description="Detect rage clicks, dead clicks, form abandonment and other issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Session ID to analyze"}
                },
                "required": ["session_id"]
            }
        ),
        Tool(
            name="generate_session_summary",
            description="Generate AI-powered summary and insights for a session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Session ID to summarize"}
                },
                "required": ["session_id"]
            }
        ),
        Tool(
            name="find_similar_sessions",
            description="Find sessions with similar patterns or issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "reference_session_id": {"type": "string", "description": "Reference session to find similar ones"},
                    "similarity_criteria": {"type": "string", "enum": ["errors", "journey", "duration", "user_behavior"], "default": "errors"}
                },
                "required": ["reference_session_id"]
            }
        ),
        Tool(
            name="get_user_session_history",
            description="Get all sessions for a specific user to analyze behavior patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID to analyze"},
                    "limit": {"type": "integer", "default": 20, "description": "Number of sessions to return"}
                },
                "required": ["user_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls for session analysis"""
    
    try:
        if name == "search_sessions":
            result = await openreplay_client.search_sessions(**arguments)
            sessions = result.get('sessions', [])
            
            summary = f"Found {len(sessions)} sessions matching criteria:\n\n"
            for session in sessions[:10]:  # Show first 10
                summary += f"• Session {session.get('id')}: {session.get('duration', 0)/1000:.1f}s"
                if session.get('user_id'):
                    summary += f" (User: {session.get('user_id')})"
                if session.get('errors_count', 0) > 0:
                    summary += f" ⚠️ {session.get('errors_count')} errors"
                summary += f" - {session.get('created_at', 'Unknown date')}\n"
            
            return [TextContent(type="text", text=summary)]
        
        elif name == "get_session_details":
            session_id = arguments["session_id"]
            session_data = await openreplay_client.get_session_details(session_id)
            
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
            
            return [TextContent(type="text", text=details)]
        
        elif name == "analyze_user_journey":
            session_id = arguments["session_id"]
            session_data = await openreplay_client.get_session_details(session_id)
            events_data = await openreplay_client.get_session_events(session_id)
            
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
            
            return [TextContent(type="text", text=analysis)]
        
        elif name == "detect_problem_patterns":
            session_id = arguments["session_id"]
            session_data = await openreplay_client.get_session_details(session_id)
            events_data = await openreplay_client.get_session_events(session_id)
            
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
            
            return [TextContent(type="text", text=report)]
        
        elif name == "generate_session_summary":
            session_id = arguments["session_id"]
            session_data = await openreplay_client.get_session_details(session_id)
            events_data = await openreplay_client.get_session_events(session_id)
            
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
            
            return [TextContent(type="text", text=summary)]
        
        elif name == "find_similar_sessions":
            reference_id = arguments["reference_session_id"]
            criteria = arguments.get("similarity_criteria", "errors")
            
            # Get reference session
            ref_session = await openreplay_client.get_session_details(reference_id)
            
            # Search for similar sessions based on criteria
            search_params = {"limit": 20}
            if criteria == "errors" and ref_session.get('errors_count', 0) > 0:
                search_params["has_errors"] = True
            elif criteria == "duration":
                duration = ref_session.get('duration', 0)
                search_params["min_duration"] = max(0, duration // 1000 - 30)  # Within 30 seconds
            
            similar_sessions = await openreplay_client.search_sessions(**search_params)
            sessions = similar_sessions.get('sessions', [])
            
            result = f"Similar Sessions to {reference_id} (by {criteria}):\n\n"
            for session in sessions[:10]:
                if session.get('id') != reference_id:  # Exclude reference session
                    result += f"• {session.get('id')}: {session.get('duration', 0)/1000:.1f}s"
                    if session.get('errors_count', 0) > 0:
                        result += f" ({session['errors_count']} errors)"
                    result += f" - {session.get('created_at', 'Unknown')}\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_user_session_history":
            user_id = arguments["user_id"]
            limit = arguments.get("limit", 20)
            
            user_sessions = await openreplay_client.get_user_sessions(user_id, limit)
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
            
            return [TextContent(type="text", text=history)]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]

@server.list_prompts()
async def list_prompts() -> List[Prompt]:
    """List available analysis prompts"""
    return [
        Prompt(
            name="debug_session",
            description="Debug a problematic session and identify issues",
            arguments=[
                {"name": "session_id", "description": "Session ID to debug", "required": True}
            ]
        ),
        Prompt(
            name="analyze_user_behavior",
            description="Analyze user behavior patterns across multiple sessions",
            arguments=[
                {"name": "user_id", "description": "User ID to analyze", "required": True}
            ]
        ),
        Prompt(
            name="ux_research_report",
            description="Generate UX research insights from session data",
            arguments=[
                {"name": "date_range", "description": "Date range for analysis (e.g., 'last_week')", "required": False}
            ]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: Dict[str, str]) -> GetPromptResult:
    """Generate analysis prompts"""
    
    if name == "debug_session":
        session_id = arguments["session_id"]
        return GetPromptResult(
            description=f"Debug session {session_id}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Please analyze session {session_id} for debugging purposes. "
                             f"I need to understand what went wrong and identify any issues. "
                             f"Use the session analysis tools to get details, detect problems, "
                             f"and generate insights about this session."
                    )
                )
            ]
        )
    
    elif name == "analyze_user_behavior":
        user_id = arguments["user_id"]
        return GetPromptResult(
            description=f"Analyze behavior for user {user_id}",
            messages=[
                PromptMessage(
                    role="user", 
                    content=TextContent(
                        type="text",
                        text=f"Please analyze the behavior patterns for user {user_id}. "
                             f"Look at their session history, identify trends, and provide "
                             f"insights about their user experience and any recurring issues."
                    )
                )
            ]
        )
    
    elif name == "ux_research_report":
        date_range = arguments.get("date_range", "last_week")
        return GetPromptResult(
            description="Generate UX research report",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text", 
                        text=f"Generate a UX research report based on session data from {date_range}. "
                             f"Search for recent sessions, identify common problems and patterns, "
                             f"and provide actionable insights for improving user experience."
                    )
                )
            ]
        )
    
    return GetPromptResult(
        description="Unknown prompt",
        messages=[PromptMessage(role="user", content=TextContent(type="text", text="Unknown prompt"))]
    )

# Django management command to run the server
class Command(BaseCommand):
    help = 'Run OpenReplay Session Analysis MCP Server'

    def handle(self, *args, **options):
        """Run the MCP server"""
        print("Starting OpenReplay Session Analysis MCP Server...")
        print(f"API URL: {config.api_url}")
        print(f"Project ID: {config.project_id}")
        
        # Run the server
        asyncio.run(server.run())

if __name__ == "__main__":
    # For direct execution
    import django
    django.setup()
    
    command = Command()
    command.handle()