"""
OpenReplay Session Analysis MCP Server
FastMCP-based server for analyzing OpenReplay session data
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import httpx


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
        self._client = None
    
    @property
    def client(self):
        """Lazy initialization of httpx AsyncClient"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={
                    'Authorization': f'Bearer {self.config.api_key}',
                    'Content-Type': 'application/json'
                },
                timeout=30.0
            )
        return self._client
    
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
    
    async def get_user_sessions(self, user_id: str, limit: int = 20) -> Dict:
        """Get all sessions for a specific user"""
        return await self.search_sessions(
            limit=limit,
            user_id=user_id
        )
    
    async def close(self):
        """Close the httpx client"""
        if self._client:
            await self._client.aclose()
            self._client = None


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


class OpenReplaySessionAnalysisTools:
    """OpenReplay Session Analysis MCP Tools"""
    
    def __init__(self):
        self.config = OpenReplayConfig()
        self.client = OpenReplayClient(self.config)
        self.analyzer = SessionAnalyzer()
    
    async def search_sessions(
        self,
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
        
        Returns:
            Formatted string with session search results
        """
        try:
            result = await self.client.search_sessions(
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
    
    async def get_session_details(self, session_id: str) -> str:
        """
        Get detailed information about a specific session.
        
        Args:
            session_id: The ID of the session to analyze
        
        Returns:
            Formatted string with detailed session information
        """
        try:
            session_data = await self.client.get_session_details(session_id)
            
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
    
    async def analyze_user_journey(self, session_id: str) -> str:
        """
        Analyze user journey and navigation patterns for a session.
        
        Args:
            session_id: The ID of the session to analyze
        
        Returns:
            Formatted string with user journey analysis
        """
        try:
            session_data = await self.client.get_session_details(session_id)
            events_data = await self.client.get_session_events(session_id)
            
            # Combine session and events data
            full_session_data = {**session_data, 'events': events_data.get('events', [])}
            journey = self.analyzer.analyze_user_journey(full_session_data)
            
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
    
    async def detect_problem_patterns(self, session_id: str) -> str:
        """
        Detect rage clicks, dead clicks, form abandonment and other issues.
        
        Args:
            session_id: The ID of the session to analyze
        
        Returns:
            Formatted string with problem pattern analysis
        """
        try:
            session_data = await self.client.get_session_details(session_id)
            events_data = await self.client.get_session_events(session_id)
            
            full_session_data = {**session_data, 'events': events_data.get('events', [])}
            problems = self.analyzer.detect_problem_patterns(full_session_data)
            
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
    
    async def generate_session_summary(self, session_id: str) -> str:
        """
        Generate AI-powered summary and insights for a session.
        
        Args:
            session_id: The ID of the session to summarize
        
        Returns:
            Formatted string with session summary and insights
        """
        try:
            session_data = await self.client.get_session_details(session_id)
            events_data = await self.client.get_session_events(session_id)
            
            full_session_data = {**session_data, 'events': events_data.get('events', [])}
            journey = self.analyzer.analyze_user_journey(full_session_data)
            problems = self.analyzer.detect_problem_patterns(full_session_data)
            insights = self.analyzer.generate_session_insights(full_session_data, problems, journey)
            
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
    
    async def find_similar_sessions(
        self, 
        reference_session_id: str, 
        similarity_criteria: str = "errors"
    ) -> str:
        """
        Find sessions with similar patterns or issues.
        
        Args:
            reference_session_id: Reference session to find similar ones
            similarity_criteria: Criteria for similarity (errors, journey, duration, user_behavior)
        
        Returns:
            Formatted string with similar sessions
        """
        try:
            # Get reference session
            ref_session = await self.client.get_session_details(reference_session_id)
            
            # Search for similar sessions based on criteria
            search_params = {"limit": 20}
            if similarity_criteria == "errors" and ref_session.get('errors_count', 0) > 0:
                search_params["has_errors"] = True
            elif similarity_criteria == "duration":
                duration = ref_session.get('duration', 0)
                search_params["min_duration"] = max(0, duration // 1000 - 30)  # Within 30 seconds
            
            similar_sessions = await self.client.search_sessions(**search_params)
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
    
    async def get_user_session_history(self, user_id: str, limit: int = 20) -> str:
        """
        Get all sessions for a specific user to analyze behavior patterns.
        
        Args:
            user_id: The ID of the user to analyze
            limit: Number of sessions to return (default: 20)
        
        Returns:
            Formatted string with user session history
        """
        try:
            user_sessions = await self.client.get_user_sessions(user_id, limit)
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


# Export the toolset for Django MCP Server
openreplay_tools = OpenReplaySessionAnalysisTools()
