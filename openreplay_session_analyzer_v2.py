"""
OpenReplay Session Analysis MCP Server - Version 2
Enhanced version using internal API endpoints from OpenReplay codebase
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

import httpx


@dataclass
class OpenReplayConfig:
    """OpenReplay API configuration"""
    api_url: str = os.getenv('OPENREPLAY_API_URL', 'https://api.openreplay.com')
    api_key: str = os.getenv('OPENREPLAY_API_KEY', '')
    project_id: str = os.getenv('OPENREPLAY_PROJECT_KEY', os.getenv('OPENREPLAY_PROJECT_ID', ''))


class OpenReplayAdvancedClient:
    """Enhanced client for OpenReplay API with internal endpoints"""
    
    def __init__(self, config: OpenReplayConfig):
        self.config = config
        self._client = None
    
    @property
    def client(self):
        """Lazy initialization of httpx AsyncClient"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={
                    'Authorization': self.config.api_key,
                    'Content-Type': 'application/json'
                },
                timeout=30.0
            )
        return self._client
    
    async def search_sessions(self, 
                            filters: List[Dict] = None,
                            start_timestamp: Optional[int] = None,
                            end_timestamp: Optional[int] = None,
                            limit: int = 50,
                            page: int = 1,
                            sort: str = "startTs",
                            order: str = "DESC") -> Dict:
        """
        Search sessions with advanced filtering
        
        Filter examples:
        - User filter: {"is_event": False, "type": "userId", "operator": "is", "value": ["user123"]}
        - Duration filter: {"is_event": False, "type": "duration", "operator": "is", "value": [5000]}
        - Error filter: {"is_event": False, "type": "errorsCount", "operator": "is", "value": [0]}
        """
        # Default time range: last 7 days
        if not start_timestamp:
            start_timestamp = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)
        if not end_timestamp:
            end_timestamp = int(datetime.now().timestamp() * 1000)
        
        payload = {
            "startTimestamp": start_timestamp,
            "endTimestamp": end_timestamp,
            "filters": filters or [],
            "events": [],
            "limit": limit,
            "page": page,
            "sort": sort,
            "order": order,
            "group_by_user": False,
            "bookmarked": False
        }
        
        response = await self.client.post(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/sessions/search",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def get_session_replay(self, session_id: str) -> Dict:
        """Get complete session replay data including events and DOM mutations"""
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/sessions/{session_id}/replay"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_session_events(self, session_id: str) -> Dict:
        """Get high-level events for a session"""
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/sessions/{session_id}/events"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_live_sessions(self, filters: List[Dict] = None) -> Dict:
        """
        Get currently active live sessions
        
        Filter examples:
        - User filter: {"type": "userId", "value": "user123", "operator": "contains"}
        - Browser filter: {"type": "userBrowser", "value": "Chrome", "operator": "is"}
        """
        payload = {
            "filters": filters or [],
            "sort": "TIMESTAMP",
            "order": "DESC",
            "limit": 50,
            "page": 1
        }
        
        response = await self.client.post(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/assist/sessions",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def get_live_session_details(self, session_id: str) -> Dict:
        """Get details for a specific live session"""
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/assist/sessions/{session_id}"
        )
        response.raise_for_status()
        return response.json()
    
    async def create_session_note(self, session_id: str, message: str, 
                                 timestamp: int = -1, is_public: bool = False,
                                 tag: Optional[str] = None) -> Dict:
        """Create a note for a session"""
        payload = {
            "message": message,
            "timestamp": timestamp,
            "is_public": is_public,
            "tag": tag
        }
        
        response = await self.client.post(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/sessions/{session_id}/notes",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def get_session_notes(self, session_id: str) -> Dict:
        """Get all notes for a session"""
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/sessions/{session_id}/notes"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_session_heatmap(self, session_id: str, url: str) -> Dict:
        """Get heatmap data for a specific URL in a session"""
        payload = {"url": url}
        
        response = await self.client.post(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/sessions/{session_id}/heatmaps",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def get_error_details(self, error_id: str) -> Dict:
        """Get details for a specific error"""
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/errors/{error_id}"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_error_sessions(self, error_id: str, start_date: Optional[int] = None,
                                end_date: Optional[int] = None) -> Dict:
        """Get all sessions that encountered a specific error"""
        params = {}
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/errors/{error_id}/sessions",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the httpx client"""
        if self._client:
            await self._client.aclose()
            self._client = None


class AdvancedSessionAnalyzer:
    """Advanced analyzer with pattern detection and ML-like insights"""
    
    @staticmethod
    def analyze_session_patterns(sessions: List[Dict]) -> Dict:
        """Analyze patterns across multiple sessions"""
        if not sessions:
            return {"error": "No sessions to analyze"}
        
        patterns = {
            "common_errors": {},
            "common_pages": {},
            "avg_duration": 0,
            "avg_pages": 0,
            "avg_events": 0,
            "browsers": {},
            "devices": {},
            "countries": {},
            "issue_types": {},
            "sessions_with_errors": 0
        }
        
        total_duration = 0
        total_pages = 0
        total_events = 0
        
        for session in sessions:
            # Duration analysis
            duration = session.get('duration', 0)
            total_duration += duration
            
            # Page analysis
            pages = session.get('pagesCount', 0)
            total_pages += pages
            
            # Event analysis
            events = session.get('eventsCount', 0)
            total_events += events
            
            # Error analysis
            if session.get('errorsCount', 0) > 0:
                patterns['sessions_with_errors'] += 1
            
            # Browser distribution
            browser = session.get('userBrowser', 'Unknown')
            patterns['browsers'][browser] = patterns['browsers'].get(browser, 0) + 1
            
            # Device distribution
            device = session.get('userDevice', 'Desktop')
            patterns['devices'][device] = patterns['devices'].get(device, 0) + 1
            
            # Country distribution
            country = session.get('userCountry', 'Unknown')
            patterns['countries'][country] = patterns['countries'].get(country, 0) + 1
            
            # Issue types
            for issue in session.get('issueTypes', []):
                patterns['issue_types'][issue] = patterns['issue_types'].get(issue, 0) + 1
        
        # Calculate averages
        num_sessions = len(sessions)
        patterns['avg_duration'] = total_duration / num_sessions if num_sessions > 0 else 0
        patterns['avg_pages'] = total_pages / num_sessions if num_sessions > 0 else 0
        patterns['avg_events'] = total_events / num_sessions if num_sessions > 0 else 0
        patterns['error_rate'] = (patterns['sessions_with_errors'] / num_sessions * 100) if num_sessions > 0 else 0
        
        return patterns
    
    @staticmethod
    def generate_insights(patterns: Dict) -> List[str]:
        """Generate actionable insights from patterns"""
        insights = []
        
        # Duration insights
        avg_duration_min = patterns.get('avg_duration', 0) / 60000
        if avg_duration_min < 1:
            insights.append(f"⚠️ Very short average session duration ({avg_duration_min:.1f} min) - users may be bouncing quickly")
        elif avg_duration_min > 30:
            insights.append(f"✅ Long average session duration ({avg_duration_min:.1f} min) - high user engagement")
        
        # Error rate insights
        error_rate = patterns.get('error_rate', 0)
        if error_rate > 50:
            insights.append(f"🚨 High error rate ({error_rate:.1f}%) - critical issues affecting majority of sessions")
        elif error_rate > 20:
            insights.append(f"⚠️ Moderate error rate ({error_rate:.1f}%) - some users experiencing issues")
        elif error_rate > 0:
            insights.append(f"ℹ️ Low error rate ({error_rate:.1f}%) - occasional issues")
        else:
            insights.append("✅ No errors detected - stable experience")
        
        # Browser insights
        browsers = patterns.get('browsers', {})
        if browsers:
            top_browser = max(browsers, key=browsers.get)
            browser_pct = (browsers[top_browser] / sum(browsers.values()) * 100)
            insights.append(f"📊 {top_browser} is the dominant browser ({browser_pct:.1f}% of sessions)")
        
        # Geographic insights
        countries = patterns.get('countries', {})
        if len(countries) > 5:
            insights.append(f"🌍 Global user base detected ({len(countries)} countries)")
        
        # Page engagement
        avg_pages = patterns.get('avg_pages', 0)
        if avg_pages < 2:
            insights.append("📄 Low page engagement - users visiting few pages per session")
        elif avg_pages > 10:
            insights.append("📚 High page engagement - users exploring extensively")
        
        # Issue type insights
        issue_types = patterns.get('issue_types', {})
        if issue_types:
            top_issue = max(issue_types, key=issue_types.get)
            insights.append(f"⚠️ Most common issue: {top_issue} ({issue_types[top_issue]} occurrences)")
        
        return insights


class OpenReplaySessionAnalysisToolsV2:
    """Enhanced OpenReplay Session Analysis MCP Tools"""
    
    def __init__(self):
        self.config = OpenReplayConfig()
        self.client = OpenReplayAdvancedClient(self.config)
        self.analyzer = AdvancedSessionAnalyzer()
    
    async def search_user_sessions(self, user_id: str, days_back: int = 7,
                                  include_errors_only: bool = False) -> str:
        """
        Search and analyze sessions for a specific user
        
        Args:
            user_id: The user ID to search for
            days_back: Number of days to look back (default: 7)
            include_errors_only: Only include sessions with errors
        
        Returns:
            Formatted analysis of user sessions
        """
        try:
            # Build filters
            filters = [
                {
                    "is_event": False,
                    "type": "userId",
                    "operator": "is",
                    "value": [user_id]
                }
            ]
            
            if include_errors_only:
                filters.append({
                    "is_event": False,
                    "type": "errorsCount",
                    "operator": ">",
                    "value": [0]
                })
            
            # Calculate timestamps
            start_timestamp = int((datetime.now() - timedelta(days=days_back)).timestamp() * 1000)
            end_timestamp = int(datetime.now().timestamp() * 1000)
            
            # Search sessions
            result = await self.client.search_sessions(
                filters=filters,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                limit=100
            )
            
            sessions = result.get('data', {}).get('sessions', [])
            total = result.get('data', {}).get('total', 0)
            
            # Analyze patterns
            patterns = self.analyzer.analyze_session_patterns(sessions)
            insights = self.analyzer.generate_insights(patterns)
            
            # Format output
            output = f"User Session Analysis for {user_id}\n"
            output += f"{'=' * 50}\n\n"
            output += f"📊 Summary (Last {days_back} days):\n"
            output += f"• Total Sessions: {total}\n"
            output += f"• Sessions Analyzed: {len(sessions)}\n"
            output += f"• Average Duration: {patterns['avg_duration']/60000:.1f} minutes\n"
            output += f"• Average Pages/Session: {patterns['avg_pages']:.1f}\n"
            output += f"• Error Rate: {patterns['error_rate']:.1f}%\n\n"
            
            output += f"🔍 Insights:\n"
            for insight in insights:
                output += f"{insight}\n"
            
            output += f"\n📱 Browser Distribution:\n"
            for browser, count in patterns['browsers'].items():
                pct = (count / len(sessions) * 100) if sessions else 0
                output += f"• {browser}: {count} ({pct:.1f}%)\n"
            
            if patterns['issue_types']:
                output += f"\n⚠️ Issues Detected:\n"
                for issue, count in patterns['issue_types'].items():
                    output += f"• {issue}: {count} occurrences\n"
            
            output += f"\n📋 Recent Sessions:\n"
            for i, session in enumerate(sessions[:5], 1):
                duration_min = session.get('duration', 0) / 60000
                output += f"{i}. Session {session['sessionId']}\n"
                output += f"   Duration: {duration_min:.1f} min | "
                output += f"Pages: {session.get('pagesCount', 0)} | "
                output += f"Errors: {session.get('errorsCount', 0)}\n"
                
                start_ts = session.get('startTs')
                if start_ts:
                    dt = datetime.fromtimestamp(start_ts / 1000)
                    output += f"   Date: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            return output
            
        except Exception as e:
            return f"Error searching user sessions: {str(e)}"
    
    async def analyze_live_sessions(self) -> str:
        """
        Get and analyze currently active live sessions
        
        Returns:
            Formatted analysis of live sessions
        """
        try:
            result = await self.client.get_live_sessions()
            sessions = result.get('data', {}).get('sessions', [])
            total = result.get('data', {}).get('total', 0)
            
            output = f"Live Session Analysis\n"
            output += f"{'=' * 50}\n\n"
            output += f"🔴 Active Sessions: {total}\n\n"
            
            if sessions:
                # Group by browser
                browsers = {}
                for session in sessions:
                    browser = session.get('userBrowser', 'Unknown')
                    browsers[browser] = browsers.get(browser, 0) + 1
                
                output += f"📱 Browser Distribution:\n"
                for browser, count in browsers.items():
                    output += f"• {browser}: {count} sessions\n"
                
                output += f"\n📋 Active Users:\n"
                for i, session in enumerate(sessions[:10], 1):
                    output += f"{i}. User: {session.get('userId', 'Anonymous')}\n"
                    output += f"   Session: {session['sessionId']}\n"
                    output += f"   Browser: {session.get('userBrowser', 'Unknown')} | "
                    output += f"OS: {session.get('userOs', 'Unknown')}\n"
                    
                    if session.get('metadata'):
                        output += f"   Metadata: {json.dumps(session['metadata'], indent=2)}\n"
            else:
                output += "No active sessions at the moment."
            
            return output
            
        except Exception as e:
            return f"Error getting live sessions: {str(e)}"
    
    async def get_session_replay_analysis(self, session_id: str) -> str:
        """
        Get detailed replay analysis for a specific session
        
        Args:
            session_id: The session ID to analyze
        
        Returns:
            Formatted replay analysis
        """
        try:
            # Get replay data
            replay_result = await self.client.get_session_replay(session_id)
            replay_data = replay_result.get('data', {})
            
            # Get events
            events_result = await self.client.get_session_events(session_id)
            events = events_result.get('data', [])
            
            output = f"Session Replay Analysis: {session_id}\n"
            output += f"{'=' * 50}\n\n"
            
            # Session info
            session = replay_data.get('session', {})
            output += f"📊 Session Info:\n"
            output += f"• Duration: {session.get('duration', 0)/60000:.1f} minutes\n"
            output += f"• User: {session.get('userId', 'Anonymous')}\n"
            
            # Event analysis
            event_types = {}
            for event in events:
                event_type = event.get('type', 'unknown')
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            output += f"\n📈 Event Summary ({len(events)} total events):\n"
            for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True):
                output += f"• {event_type}: {count} events\n"
            
            # Key events timeline
            output += f"\n⏱️ Key Events Timeline:\n"
            key_events = [e for e in events if e.get('type') in ['click', 'error', 'custom', 'location']]
            for i, event in enumerate(key_events[:10], 1):
                timestamp = event.get('timestamp', 0)
                time_str = f"{timestamp/1000:.1f}s"
                output += f"{i}. [{time_str}] {event.get('type', 'unknown')}"
                
                if event.get('element'):
                    output += f" on {event['element']}"
                if event.get('url'):
                    output += f" at {event['url']}"
                output += "\n"
            
            # Errors if any
            errors = replay_data.get('errors', [])
            if errors:
                output += f"\n🐛 Errors Detected ({len(errors)}):\n"
                for i, error in enumerate(errors[:5], 1):
                    output += f"{i}. {error.get('message', 'Unknown error')}\n"
                    output += f"   Stack: {error.get('stack', 'N/A')[:100]}...\n"
            
            return output
            
        except Exception as e:
            return f"Error analyzing session replay: {str(e)}"
    
    async def close(self):
        """Clean up resources"""
        await self.client.close()


# Export for MCP usage
openreplay_tools_v2 = OpenReplaySessionAnalysisToolsV2()