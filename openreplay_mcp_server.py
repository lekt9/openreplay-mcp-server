"""
OpenReplay MCP Server - Complete Implementation
Provides comprehensive session analysis, monitoring, and debugging capabilities
"""

import os
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

import httpx
from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field


# ============================================================================
# Configuration and Enums
# ============================================================================

@dataclass
class OpenReplayConfig:
    """OpenReplay API configuration"""
    api_url: str = os.getenv('OPENREPLAY_API_URL', 'https://api.openreplay.com')
    api_key: str = os.getenv('OPENREPLAY_API_KEY', '')
    project_id: str = os.getenv('OPENREPLAY_PROJECT_KEY', os.getenv('OPENREPLAY_PROJECT_ID', ''))


class FilterType(str, Enum):
    """Session filter types"""
    USERID = "userId"
    USER_BROWSER = "userBrowser"
    USER_OS = "userOs"
    USER_DEVICE = "userDevice"
    USER_COUNTRY = "userCountry"
    PLATFORM = "platform"
    DURATION = "duration"
    ERRORS_COUNT = "errorsCount"
    EVENTS_COUNT = "eventsCount"
    PAGES_COUNT = "pagesCount"
    ISSUE = "issue"
    METADATA = "metadata"


class EventType(str, Enum):
    """Event types for filtering"""
    CLICK = "click"
    INPUT = "input"
    LOCATION = "location"
    CUSTOM = "custom"
    ERROR = "error"
    PAGE_VIEW = "page_view"
    FORM_SUBMIT = "submit"


class SearchOperator(str, Enum):
    """Search operators"""
    IS = "is"
    IS_NOT = "isNot"
    CONTAINS = "contains"
    NOT_CONTAINS = "notContains"
    STARTS_WITH = "startsWith"
    ENDS_WITH = "endsWith"
    GREATER = ">"
    LESS = "<"


class SortOrder(str, Enum):
    """Sort order options"""
    ASC = "ASC"
    DESC = "DESC"


class IssueType(str, Enum):
    """Issue types"""
    RAGE_CLICK = "rage_click"
    DEAD_CLICK = "dead_click"
    EXCESSIVE_SCROLLING = "excessive_scrolling"
    BAD_REQUEST = "bad_request"
    MISSING_RESOURCE = "missing_resource"
    MEMORY = "memory"
    CPU = "cpu"
    SLOW_RESOURCE = "slow_resource"
    CRASH = "crash"


# ============================================================================
# API Client
# ============================================================================

class OpenReplayClient:
    """Complete OpenReplay API client with all capabilities"""
    
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
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout=30.0
            )
        return self._client
    
    # ========== Session Search and Analysis ==========
    
    async def search_sessions(self,
                            filters: List[Dict] = None,
                            events: List[Dict] = None,
                            start_timestamp: Optional[int] = None,
                            end_timestamp: Optional[int] = None,
                            limit: int = 50,
                            page: int = 1,
                            sort: str = "startTs",
                            order: str = "DESC",
                            group_by_user: bool = False,
                            bookmarked: bool = False) -> Dict:
        """Search sessions with advanced filtering and event correlation"""
        
        if not start_timestamp:
            start_timestamp = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)
        if not end_timestamp:
            end_timestamp = int(datetime.now().timestamp() * 1000)
        
        payload = {
            "startTimestamp": start_timestamp,
            "endTimestamp": end_timestamp,
            "filters": filters or [],
            "events": events or [],
            "limit": limit,
            "page": page,
            "sort": sort,
            "order": order,
            "group_by_user": group_by_user,
            "bookmarked": bookmarked
        }
        
        response = await self.client.post(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/sessions/search",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def get_session_ids(self, filters: List[Dict] = None, **kwargs) -> Dict:
        """Get only session IDs matching the search criteria"""
        payload = {
            "filters": filters or [],
            **kwargs
        }
        
        response = await self.client.post(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/sessions/search/ids",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    # ========== Session Replay and Events ==========
    
    async def get_session_replay(self, session_id: str) -> Dict:
        """Get complete session replay data"""
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
    
    async def get_first_mob(self, session_id: str) -> Dict:
        """Get initial session data for quick loading"""
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/sessions/{session_id}/first-mob"
        )
        response.raise_for_status()
        return response.json()
    
    # ========== Live Sessions (Assist) ==========
    
    async def get_live_sessions(self, filters: List[Dict] = None,
                               sort: str = "TIMESTAMP",
                               order: str = "DESC",
                               limit: int = 50,
                               page: int = 1) -> Dict:
        """Get currently active live sessions"""
        payload = {
            "filters": filters or [],
            "sort": sort,
            "order": order,
            "limit": limit,
            "page": page
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
    
    # ========== User Analysis ==========
    
    async def get_user_sessions(self, user_id: str,
                               start_date: Optional[int] = None,
                               end_date: Optional[int] = None) -> Dict:
        """Get all sessions for a specific user"""
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/users/{user_id}/sessions",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def get_user_stats(self, user_id: str) -> Dict:
        """Get statistics for a specific user"""
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/users/{user_id}"
        )
        response.raise_for_status()
        return response.json()
    
    # ========== Error Analysis ==========
    
    async def search_errors(self, filters: List[Dict] = None,
                           start_timestamp: Optional[int] = None,
                           end_timestamp: Optional[int] = None,
                           limit: int = 50,
                           page: int = 1,
                           sort: str = "occurrence",
                           order: str = "DESC") -> Dict:
        """Search for errors with filtering"""
        payload = {
            "startTimestamp": start_timestamp,
            "endTimestamp": end_timestamp,
            "filters": filters or [],
            "limit": limit,
            "page": page,
            "sort": sort,
            "order": order
        }
        
        response = await self.client.post(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/errors/search",
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
    
    async def get_error_sessions(self, error_id: str,
                                start_date: Optional[int] = None,
                                end_date: Optional[int] = None,
                                action: str = "ALL") -> Dict:
        """Get sessions that encountered a specific error"""
        params = {"action": action}
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
    
    async def get_error_trace(self, session_id: str, error_id: str) -> Dict:
        """Get error stack trace with sourcemaps applied"""
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/sessions/{session_id}/errors/{error_id}/sourcemaps"
        )
        response.raise_for_status()
        return response.json()
    
    # ========== Notes and Annotations ==========
    
    async def create_session_note(self, session_id: str,
                                 message: str,
                                 timestamp: int = -1,
                                 is_public: bool = False,
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
    
    async def update_session_note(self, session_id: str, note_id: str,
                                 message: Optional[str] = None,
                                 timestamp: Optional[int] = None,
                                 is_public: Optional[bool] = None) -> Dict:
        """Update an existing session note"""
        payload = {}
        if message is not None:
            payload["message"] = message
        if timestamp is not None:
            payload["timestamp"] = timestamp
        if is_public is not None:
            payload["is_public"] = is_public
        
        response = await self.client.put(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/sessions/{session_id}/notes/{note_id}",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def delete_session_note(self, session_id: str, note_id: str) -> Dict:
        """Delete a session note"""
        response = await self.client.delete(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/sessions/{session_id}/notes/{note_id}"
        )
        response.raise_for_status()
        return response.json()
    
    async def search_notes(self, query: str, limit: int = 50) -> Dict:
        """Search across all session notes"""
        payload = {
            "query": query,
            "limit": limit
        }
        
        response = await self.client.post(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/notes",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    # ========== Heatmaps and Analytics ==========
    
    async def get_session_heatmap(self, session_id: str, url: str) -> Dict:
        """Get heatmap data for a specific URL in a session"""
        payload = {"url": url}
        
        response = await self.client.post(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/sessions/{session_id}/heatmaps",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def get_session_clickmap(self, session_id: str, url: str) -> Dict:
        """Get clickmap data for a specific URL in a session"""
        payload = {"url": url}
        
        response = await self.client.post(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/sessions/{session_id}/clickmaps",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    # ========== Favorites and Assignments ==========
    
    async def toggle_favorite_session(self, session_id: str) -> Dict:
        """Add or remove a session from favorites"""
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/sessions/{session_id}/favorite"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_session_assignments(self, session_id: str) -> Dict:
        """Get issue tracking assignments for a session"""
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/sessions/{session_id}/assign"
        )
        response.raise_for_status()
        return response.json()
    
    # ========== Metadata and Autocomplete ==========
    
    async def autocomplete(self, query: str, type: Optional[str] = None,
                          key: Optional[str] = None, source: Optional[str] = None,
                          live: bool = False) -> Dict:
        """Autocomplete for filters and search"""
        params = {"q": query}
        if type:
            params["type"] = type
        if key:
            params["key"] = key
        if source:
            params["source"] = source
        if live:
            params["live"] = str(live).lower()
        
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/autocomplete",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def get_metadata(self) -> Dict:
        """Get metadata for the project"""
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/metadata"
        )
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the httpx client"""
        if self._client:
            await self._client.aclose()
            self._client = None


# ============================================================================
# Analysis Engine
# ============================================================================

class SessionAnalyzer:
    """Advanced session analysis engine"""
    
    @staticmethod
    def analyze_session_patterns(sessions: List[Dict]) -> Dict:
        """Analyze patterns across multiple sessions"""
        if not sessions:
            return {"error": "No sessions to analyze"}
        
        patterns = {
            "total_sessions": len(sessions),
            "user_metrics": {},
            "technical_metrics": {},
            "engagement_metrics": {},
            "issue_analysis": {},
            "time_patterns": {}
        }
        
        # Initialize counters
        total_duration = 0
        total_pages = 0
        total_events = 0
        sessions_with_errors = 0
        browsers = {}
        devices = {}
        countries = {}
        platforms = {}
        issue_types = {}
        hourly_distribution = [0] * 24
        
        for session in sessions:
            # Duration and engagement
            duration = session.get('duration', 0)
            total_duration += duration
            total_pages += session.get('pagesCount', 0)
            total_events += session.get('eventsCount', 0)
            
            # Error tracking
            if session.get('errorsCount', 0) > 0:
                sessions_with_errors += 1
            
            # Technical distribution
            browser = session.get('userBrowser', 'Unknown')
            browsers[browser] = browsers.get(browser, 0) + 1
            
            device = session.get('userDevice', 'Desktop') or 'Desktop'
            devices[device] = devices.get(device, 0) + 1
            
            platform = session.get('platform', 'web')
            platforms[platform] = platforms.get(platform, 0) + 1
            
            # Geographic distribution
            country = session.get('userCountry', 'Unknown')
            countries[country] = countries.get(country, 0) + 1
            
            # Issue types
            for issue in session.get('issueTypes', []):
                issue_types[issue] = issue_types.get(issue, 0) + 1
            
            # Time patterns
            if session.get('startTs'):
                hour = datetime.fromtimestamp(session['startTs'] / 1000).hour
                hourly_distribution[hour] += 1
        
        # Calculate metrics
        num_sessions = len(sessions)
        
        # User metrics
        patterns['user_metrics'] = {
            'unique_users': len(set(s.get('userId', s.get('userUuid', '')) for s in sessions)),
            'avg_sessions_per_user': num_sessions / max(1, patterns['user_metrics'].get('unique_users', 1)),
            'geographic_distribution': countries,
            'top_countries': sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]
        }
        
        # Technical metrics
        patterns['technical_metrics'] = {
            'browsers': browsers,
            'devices': devices,
            'platforms': platforms,
            'top_browser': max(browsers, key=browsers.get) if browsers else 'Unknown',
            'mobile_percentage': (devices.get('Mobile', 0) / num_sessions * 100) if num_sessions > 0 else 0
        }
        
        # Engagement metrics
        patterns['engagement_metrics'] = {
            'avg_duration': total_duration / num_sessions if num_sessions > 0 else 0,
            'avg_pages': total_pages / num_sessions if num_sessions > 0 else 0,
            'avg_events': total_events / num_sessions if num_sessions > 0 else 0,
            'bounce_rate': sum(1 for s in sessions if s.get('pagesCount', 0) <= 1) / num_sessions * 100 if num_sessions > 0 else 0,
            'high_engagement_sessions': sum(1 for s in sessions if s.get('duration', 0) > 300000)  # > 5 minutes
        }
        
        # Issue analysis
        patterns['issue_analysis'] = {
            'error_rate': (sessions_with_errors / num_sessions * 100) if num_sessions > 0 else 0,
            'sessions_with_errors': sessions_with_errors,
            'issue_types': issue_types,
            'critical_issues': {k: v for k, v in issue_types.items() if v > num_sessions * 0.1}  # Issues affecting > 10% of sessions
        }
        
        # Time patterns
        patterns['time_patterns'] = {
            'hourly_distribution': hourly_distribution,
            'peak_hours': sorted(enumerate(hourly_distribution), key=lambda x: x[1], reverse=True)[:3],
            'date_range': {
                'start': min((s.get('startTs', float('inf')) for s in sessions), default=None),
                'end': max((s.get('startTs', 0) for s in sessions), default=None)
            }
        }
        
        return patterns
    
    @staticmethod
    def generate_insights(patterns: Dict) -> List[str]:
        """Generate actionable insights from patterns"""
        insights = []
        
        # User insights
        user_metrics = patterns.get('user_metrics', {})
        if user_metrics.get('unique_users', 0) > 0:
            avg_sessions = user_metrics.get('avg_sessions_per_user', 0)
            if avg_sessions > 3:
                insights.append(f"🎯 High user engagement with {avg_sessions:.1f} sessions per user")
            elif avg_sessions < 1.5:
                insights.append(f"⚠️ Low return rate with only {avg_sessions:.1f} sessions per user")
        
        # Geographic insights
        top_countries = user_metrics.get('top_countries', [])
        if len(top_countries) > 0:
            top_country = top_countries[0]
            if len(user_metrics.get('geographic_distribution', {})) > 10:
                insights.append(f"🌍 Global reach with users from {len(user_metrics['geographic_distribution'])} countries")
            else:
                insights.append(f"📍 Concentrated user base - {top_country[0]} accounts for {top_country[1]} sessions")
        
        # Technical insights
        tech_metrics = patterns.get('technical_metrics', {})
        mobile_pct = tech_metrics.get('mobile_percentage', 0)
        if mobile_pct > 50:
            insights.append(f"📱 Mobile-first usage pattern ({mobile_pct:.1f}% mobile sessions)")
        elif mobile_pct < 20:
            insights.append(f"💻 Desktop-dominated usage ({100-mobile_pct:.1f}% desktop sessions)")
        
        # Engagement insights
        engagement = patterns.get('engagement_metrics', {})
        avg_duration_min = engagement.get('avg_duration', 0) / 60000
        if avg_duration_min < 1:
            insights.append(f"⚡ Very short sessions ({avg_duration_min:.1f} min avg) - possible UX issues")
        elif avg_duration_min > 10:
            insights.append(f"⏰ Long engagement sessions ({avg_duration_min:.1f} min avg)")
        
        bounce_rate = engagement.get('bounce_rate', 0)
        if bounce_rate > 70:
            insights.append(f"🔴 High bounce rate ({bounce_rate:.1f}%) - landing page optimization needed")
        elif bounce_rate < 30:
            insights.append(f"✅ Excellent bounce rate ({bounce_rate:.1f}%) - good user engagement")
        
        # Issue insights
        issues = patterns.get('issue_analysis', {})
        error_rate = issues.get('error_rate', 0)
        if error_rate > 50:
            insights.append(f"🚨 Critical: {error_rate:.1f}% of sessions have errors")
        elif error_rate > 20:
            insights.append(f"⚠️ {error_rate:.1f}% error rate needs attention")
        elif error_rate > 0:
            insights.append(f"ℹ️ {error_rate:.1f}% error rate - monitor for trends")
        
        critical_issues = issues.get('critical_issues', {})
        if critical_issues:
            for issue_type, count in list(critical_issues.items())[:2]:
                insights.append(f"🔍 {issue_type.replace('_', ' ').title()} affecting {count} sessions")
        
        # Time pattern insights
        time_patterns = patterns.get('time_patterns', {})
        peak_hours = time_patterns.get('peak_hours', [])
        if peak_hours:
            peak_hour = peak_hours[0]
            insights.append(f"⏰ Peak usage at {peak_hour[0]:02d}:00 with {peak_hour[1]} sessions")
        
        return insights


# ============================================================================
# MCP Server Implementation
# ============================================================================

# Initialize MCP server
mcp = FastMCP("openreplay-session-analyzer")

# Initialize configuration and clients
config = OpenReplayConfig()
client = OpenReplayClient(config)
analyzer = SessionAnalyzer()


# ============================================================================
# MCP Tool Definitions
# ============================================================================

@mcp.tool()
async def search_sessions(
    filters: Optional[List[Dict]] = None,
    user_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
    include_errors_only: bool = False,
    sort_by: str = "startTs",
    order: str = "DESC"
) -> str:
    """
    Search and analyze OpenReplay sessions with advanced filtering.
    
    Args:
        filters: Custom filters list (optional)
        user_id: Filter by specific user ID
        start_date: Start date (YYYY-MM-DD format)
        end_date: End date (YYYY-MM-DD format)
        limit: Maximum number of sessions to return
        include_errors_only: Only include sessions with errors
        sort_by: Sort field (startTs, duration, eventsCount, errorsCount)
        order: Sort order (ASC or DESC)
    
    Returns:
        Formatted analysis of matching sessions
    """
    try:
        # Build filters
        if not filters:
            filters = []
        
        if user_id:
            filters.append({
                "is_event": False,
                "type": "userId",
                "operator": "is",
                "value": [user_id]
            })
        
        if include_errors_only:
            filters.append({
                "is_event": False,
                "type": "errorsCount",
                "operator": ">",
                "value": [0]
            })
        
        # Parse dates
        start_timestamp = None
        end_timestamp = None
        if start_date:
            start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
        if end_date:
            end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)
        
        # Search sessions
        result = await client.search_sessions(
            filters=filters,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=limit,
            sort=sort_by,
            order=order
        )
        
        sessions = result.get('data', {}).get('sessions', [])
        total = result.get('data', {}).get('total', 0)
        
        # Analyze patterns
        patterns = analyzer.analyze_session_patterns(sessions)
        insights = analyzer.generate_insights(patterns)
        
        # Format output
        output = f"📊 Session Search Results\n{'=' * 60}\n\n"
        output += f"Found {total} total sessions, analyzing {len(sessions)}\n\n"
        
        # Key metrics
        output += f"📈 Key Metrics:\n"
        engagement = patterns.get('engagement_metrics', {})
        output += f"• Avg Duration: {engagement.get('avg_duration', 0)/60000:.1f} min\n"
        output += f"• Avg Pages: {engagement.get('avg_pages', 0):.1f}\n"
        output += f"• Bounce Rate: {engagement.get('bounce_rate', 0):.1f}%\n"
        output += f"• Error Rate: {patterns.get('issue_analysis', {}).get('error_rate', 0):.1f}%\n\n"
        
        # Insights
        if insights:
            output += f"💡 Insights:\n"
            for insight in insights[:5]:
                output += f"{insight}\n"
            output += "\n"
        
        # Session list
        output += f"📋 Sessions:\n"
        for i, session in enumerate(sessions[:10], 1):
            output += f"\n{i}. Session {session['sessionId']}\n"
            output += f"   User: {session.get('userId', 'Anonymous')}\n"
            output += f"   Duration: {session.get('duration', 0)/60000:.1f} min | "
            output += f"Pages: {session.get('pagesCount', 0)} | "
            output += f"Errors: {session.get('errorsCount', 0)}\n"
            
            if session.get('startTs'):
                dt = datetime.fromtimestamp(session['startTs'] / 1000)
                output += f"   Date: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if session.get('issueTypes'):
                output += f"   Issues: {', '.join(session['issueTypes'])}\n"
        
        return output
        
    except Exception as e:
        return f"Error searching sessions: {str(e)}"


@mcp.tool()
async def get_live_sessions(
    user_id: Optional[str] = None,
    browser: Optional[str] = None
) -> str:
    """
    Get and analyze currently active live sessions.
    
    Args:
        user_id: Filter by specific user ID
        browser: Filter by browser type
    
    Returns:
        List of active live sessions with details
    """
    try:
        filters = []
        if user_id:
            filters.append({
                "type": "userId",
                "value": user_id,
                "operator": "contains"
            })
        if browser:
            filters.append({
                "type": "userBrowser",
                "value": browser,
                "operator": "is"
            })
        
        result = await client.get_live_sessions(filters=filters)
        sessions = result.get('data', {}).get('sessions', [])
        total = result.get('data', {}).get('total', 0)
        
        output = f"🔴 Live Sessions Monitor\n{'=' * 60}\n\n"
        output += f"Active Sessions: {total}\n\n"
        
        if sessions:
            # Group by status
            active_tabs = sum(1 for s in sessions if s.get('activeTab'))
            output += f"📊 Status:\n"
            output += f"• Active Tabs: {active_tabs}\n"
            output += f"• Background Tabs: {total - active_tabs}\n\n"
            
            output += f"👥 Active Users:\n"
            for i, session in enumerate(sessions, 1):
                output += f"\n{i}. {session.get('userId', 'Anonymous')}\n"
                output += f"   Session: {session['sessionId']}\n"
                output += f"   Browser: {session.get('userBrowser', 'Unknown')} on {session.get('userOs', 'Unknown')}\n"
                output += f"   Location: {session.get('userCountry', 'Unknown')}\n"
                
                if session.get('startTs'):
                    duration = (datetime.now().timestamp() * 1000 - session['startTs']) / 60000
                    output += f"   Duration: {duration:.1f} min\n"
                
                output += f"   Status: {'🟢 Active' if session.get('activeTab') else '🟡 Background'}\n"
        else:
            output += "No active sessions at the moment."
        
        return output
        
    except Exception as e:
        return f"Error getting live sessions: {str(e)}"


@mcp.tool()
async def analyze_session_replay(session_id: str) -> str:
    """
    Get detailed analysis of a session replay including events and user journey.
    
    Args:
        session_id: The session ID to analyze
    
    Returns:
        Comprehensive session replay analysis
    """
    try:
        # Get replay data and events in parallel
        replay_task = client.get_session_replay(session_id)
        events_task = client.get_session_events(session_id)
        
        replay_result = await replay_task
        events_result = await events_task
        
        replay_data = replay_result.get('data', {})
        events = events_result.get('data', [])
        
        output = f"🎬 Session Replay Analysis\n{'=' * 60}\n"
        output += f"Session ID: {session_id}\n\n"
        
        # Session info
        session = replay_data.get('session', {})
        output += f"📊 Session Overview:\n"
        output += f"• User: {session.get('userId', 'Anonymous')}\n"
        output += f"• Duration: {session.get('duration', 0)/60000:.1f} minutes\n"
        output += f"• Browser: {session.get('userBrowser', 'Unknown')} on {session.get('userOs', 'Unknown')}\n"
        output += f"• Location: {session.get('userCountry', 'Unknown')}\n\n"
        
        # Event analysis
        event_types = {}
        page_visits = []
        errors = []
        clicks = []
        
        for event in events:
            event_type = event.get('type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            if event_type == 'location':
                page_visits.append(event)
            elif event_type == 'error':
                errors.append(event)
            elif event_type == 'click':
                clicks.append(event)
        
        output += f"📈 Activity Summary ({len(events)} total events):\n"
        for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True):
            output += f"• {event_type}: {count} events\n"
        output += "\n"
        
        # User journey
        if page_visits:
            output += f"🗺️ User Journey ({len(page_visits)} pages):\n"
            for i, page in enumerate(page_visits[:10], 1):
                timestamp = page.get('timestamp', 0)
                output += f"{i}. [{timestamp/1000:.1f}s] {page.get('url', 'Unknown URL')}\n"
            output += "\n"
        
        # Key interactions
        if clicks:
            output += f"🖱️ Key Interactions ({len(clicks)} clicks):\n"
            for i, click in enumerate(clicks[:5], 1):
                timestamp = click.get('timestamp', 0)
                output += f"{i}. [{timestamp/1000:.1f}s] Clicked {click.get('element', 'unknown element')}\n"
            output += "\n"
        
        # Errors
        if errors:
            output += f"🐛 Errors Detected ({len(errors)}):\n"
            for i, error in enumerate(errors[:5], 1):
                output += f"{i}. {error.get('message', 'Unknown error')}\n"
                if error.get('stack'):
                    output += f"   Stack: {error['stack'][:100]}...\n"
            output += "\n"
        
        # Performance insights
        if replay_data.get('resources'):
            slow_resources = [r for r in replay_data['resources'] if r.get('duration', 0) > 1000]
            if slow_resources:
                output += f"⚠️ Slow Resources ({len(slow_resources)}):\n"
                for i, resource in enumerate(slow_resources[:3], 1):
                    output += f"{i}. {resource.get('name', 'Unknown')} - {resource.get('duration', 0)}ms\n"
        
        return output
        
    except Exception as e:
        return f"Error analyzing session replay: {str(e)}"


@mcp.tool()
async def search_errors(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50
) -> str:
    """
    Search and analyze errors across sessions.
    
    Args:
        start_date: Start date (YYYY-MM-DD format)
        end_date: End date (YYYY-MM-DD format)
        limit: Maximum number of errors to return
    
    Returns:
        Error analysis report
    """
    try:
        # Parse dates
        start_timestamp = None
        end_timestamp = None
        if start_date:
            start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
        if end_date:
            end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)
        
        result = await client.search_errors(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=limit
        )
        
        errors = result.get('data', {}).get('errors', [])
        total = result.get('data', {}).get('total', 0)
        
        output = f"🐛 Error Analysis Report\n{'=' * 60}\n\n"
        output += f"Found {total} unique errors\n\n"
        
        if errors:
            # Group errors by type
            error_types = {}
            for error in errors:
                error_type = error.get('type', 'Unknown')
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            output += f"📊 Error Distribution:\n"
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                output += f"• {error_type}: {count} errors\n"
            output += "\n"
            
            output += f"🔝 Top Errors:\n"
            for i, error in enumerate(errors[:10], 1):
                output += f"\n{i}. {error.get('message', 'Unknown error')}\n"
                output += f"   Error ID: {error.get('errorId', 'N/A')}\n"
                output += f"   Occurrences: {error.get('occurrence', 0)}\n"
                output += f"   Sessions Affected: {error.get('sessionsCount', 0)}\n"
                output += f"   Users Affected: {error.get('usersCount', 0)}\n"
                
                if error.get('lastOccurrence'):
                    dt = datetime.fromtimestamp(error['lastOccurrence'] / 1000)
                    output += f"   Last Seen: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
        else:
            output += "No errors found in the specified time range."
        
        return output
        
    except Exception as e:
        return f"Error searching errors: {str(e)}"


@mcp.tool()
async def get_error_details(error_id: str) -> str:
    """
    Get detailed information about a specific error.
    
    Args:
        error_id: The error ID to investigate
    
    Returns:
        Detailed error information and affected sessions
    """
    try:
        # Get error details and affected sessions
        error_task = client.get_error_details(error_id)
        sessions_task = client.get_error_sessions(error_id)
        
        error_result = await error_task
        sessions_result = await sessions_task
        
        error = error_result.get('data', {})
        sessions = sessions_result.get('data', [])
        
        output = f"🔍 Error Details\n{'=' * 60}\n\n"
        output += f"Error ID: {error_id}\n"
        output += f"Message: {error.get('message', 'Unknown')}\n"
        output += f"Type: {error.get('type', 'Unknown')}\n\n"
        
        output += f"📊 Impact:\n"
        output += f"• Total Occurrences: {error.get('occurrence', 0)}\n"
        output += f"• Sessions Affected: {error.get('sessionsCount', 0)}\n"
        output += f"• Users Affected: {error.get('usersCount', 0)}\n\n"
        
        if error.get('stack'):
            output += f"📝 Stack Trace:\n{error['stack'][:500]}\n\n"
        
        if error.get('source'):
            output += f"📍 Source:\n{error['source']}\n\n"
        
        if sessions:
            output += f"🔗 Affected Sessions ({len(sessions)} shown):\n"
            for i, session in enumerate(sessions[:5], 1):
                output += f"\n{i}. Session {session.get('sessionId', 'Unknown')}\n"
                output += f"   User: {session.get('userId', 'Anonymous')}\n"
                output += f"   Browser: {session.get('userBrowser', 'Unknown')}\n"
                
                if session.get('startTs'):
                    dt = datetime.fromtimestamp(session['startTs'] / 1000)
                    output += f"   Date: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return output
        
    except Exception as e:
        return f"Error getting error details: {str(e)}"


@mcp.tool()
async def manage_session_notes(
    session_id: str,
    action: str = "get",
    message: Optional[str] = None,
    note_id: Optional[str] = None,
    is_public: bool = False
) -> str:
    """
    Manage notes and annotations for a session.
    
    Args:
        session_id: The session ID
        action: Action to perform (get, create, update, delete)
        message: Note message (for create/update)
        note_id: Note ID (for update/delete)
        is_public: Whether the note is public
    
    Returns:
        Note operation result
    """
    try:
        if action == "get":
            result = await client.get_session_notes(session_id)
            notes = result.get('data', [])
            
            output = f"📝 Session Notes\n{'=' * 60}\n"
            output += f"Session: {session_id}\n"
            output += f"Total Notes: {len(notes)}\n\n"
            
            if notes:
                for i, note in enumerate(notes, 1):
                    output += f"{i}. {note.get('message', 'No message')}\n"
                    output += f"   By: {note.get('userName', 'Unknown')}\n"
                    output += f"   Visibility: {'Public' if note.get('isPublic') else 'Private'}\n"
                    
                    if note.get('createdAt'):
                        dt = datetime.fromtimestamp(note['createdAt'] / 1000)
                        output += f"   Created: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    
                    if note.get('tag'):
                        output += f"   Tag: {note['tag']}\n"
                    output += "\n"
            else:
                output += "No notes found for this session."
            
            return output
            
        elif action == "create" and message:
            result = await client.create_session_note(
                session_id=session_id,
                message=message,
                is_public=is_public
            )
            return f"✅ Note created successfully: {message}"
            
        elif action == "update" and note_id and message:
            result = await client.update_session_note(
                session_id=session_id,
                note_id=note_id,
                message=message,
                is_public=is_public
            )
            return f"✅ Note updated successfully"
            
        elif action == "delete" and note_id:
            result = await client.delete_session_note(
                session_id=session_id,
                note_id=note_id
            )
            return f"✅ Note deleted successfully"
            
        else:
            return "Invalid action or missing parameters. Use action='get', 'create', 'update', or 'delete'"
            
    except Exception as e:
        return f"Error managing session notes: {str(e)}"


@mcp.tool()
async def get_user_analysis(user_id: str) -> str:
    """
    Get comprehensive analysis for a specific user.
    
    Args:
        user_id: The user ID to analyze
    
    Returns:
        Complete user behavior analysis
    """
    try:
        # Get user stats and sessions
        stats_task = client.get_user_stats(user_id)
        sessions_task = client.get_user_sessions(user_id)
        
        stats_result = await stats_task
        sessions_result = await sessions_task
        
        user_data = stats_result.get('data', {})
        sessions = sessions_result.get('data', [])
        
        output = f"👤 User Analysis\n{'=' * 60}\n"
        output += f"User ID: {user_id}\n\n"
        
        output += f"📊 User Statistics:\n"
        output += f"• Total Sessions: {user_data.get('sessionCount', 0)}\n"
        
        if user_data.get('firstSeen'):
            dt = datetime.fromtimestamp(user_data['firstSeen'] / 1000)
            output += f"• First Seen: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if user_data.get('lastSeen'):
            dt = datetime.fromtimestamp(user_data['lastSeen'] / 1000)
            output += f"• Last Seen: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            # Calculate user lifetime
            if user_data.get('firstSeen'):
                lifetime_days = (user_data['lastSeen'] - user_data['firstSeen']) / (1000 * 86400)
                output += f"• User Lifetime: {lifetime_days:.0f} days\n"
        
        output += "\n"
        
        if sessions:
            # Analyze user's session patterns
            patterns = analyzer.analyze_session_patterns(sessions)
            
            output += f"📈 Behavior Patterns:\n"
            engagement = patterns.get('engagement_metrics', {})
            output += f"• Avg Session Duration: {engagement.get('avg_duration', 0)/60000:.1f} min\n"
            output += f"• Avg Pages per Session: {engagement.get('avg_pages', 0):.1f}\n"
            output += f"• Avg Events per Session: {engagement.get('avg_events', 0):.1f}\n"
            
            issues = patterns.get('issue_analysis', {})
            output += f"• Sessions with Errors: {issues.get('error_rate', 0):.1f}%\n\n"
            
            tech = patterns.get('technical_metrics', {})
            if tech.get('browsers'):
                output += f"🖥️ Browsers Used:\n"
                for browser, count in tech['browsers'].items():
                    output += f"• {browser}: {count} sessions\n"
                output += "\n"
            
            output += f"📋 Recent Sessions:\n"
            for i, session in enumerate(sessions[:5], 1):
                output += f"\n{i}. Session {session.get('sessionId', 'Unknown')}\n"
                output += f"   Duration: {session.get('duration', 0)/60000:.1f} min\n"
                output += f"   Pages: {session.get('pagesCount', 0)} | "
                output += f"   Events: {session.get('eventsCount', 0)} | "
                output += f"   Errors: {session.get('errorsCount', 0)}\n"
                
                if session.get('startTs'):
                    dt = datetime.fromtimestamp(session['startTs'] / 1000)
                    output += f"   Date: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
        else:
            output += "No sessions found for this user."
        
        return output
        
    except Exception as e:
        return f"Error analyzing user: {str(e)}"


@mcp.tool()
async def get_session_heatmap(session_id: str, url: str) -> str:
    """
    Get heatmap data for a specific URL in a session.
    
    Args:
        session_id: The session ID
        url: The URL to analyze
    
    Returns:
        Heatmap analysis for the URL
    """
    try:
        result = await client.get_session_heatmap(session_id, url)
        heatmap_data = result.get('data', {})
        
        output = f"🔥 Heatmap Analysis\n{'=' * 60}\n"
        output += f"Session: {session_id}\n"
        output += f"URL: {url}\n\n"
        
        if heatmap_data:
            clicks = heatmap_data.get('clicks', [])
            output += f"📊 Click Distribution:\n"
            output += f"• Total Clicks: {len(clicks)}\n\n"
            
            if clicks:
                # Group clicks by element
                element_clicks = {}
                for click in clicks:
                    element = click.get('selector', 'Unknown')
                    element_clicks[element] = element_clicks.get(element, 0) + 1
                
                output += f"🎯 Most Clicked Elements:\n"
                for element, count in sorted(element_clicks.items(), key=lambda x: x[1], reverse=True)[:10]:
                    output += f"• {element}: {count} clicks\n"
                
                # Analyze click positions
                if any(c.get('x') for c in clicks):
                    avg_x = sum(c.get('x', 0) for c in clicks) / len(clicks)
                    avg_y = sum(c.get('y', 0) for c in clicks) / len(clicks)
                    output += f"\n📍 Average Click Position:\n"
                    output += f"• X: {avg_x:.0f}px\n"
                    output += f"• Y: {avg_y:.0f}px\n"
        else:
            output += "No heatmap data available for this URL."
        
        return output
        
    except Exception as e:
        return f"Error getting heatmap: {str(e)}"


@mcp.tool()
async def search_notes(query: str, limit: int = 20) -> str:
    """
    Search across all session notes.
    
    Args:
        query: Search query
        limit: Maximum results to return
    
    Returns:
        Matching notes across all sessions
    """
    try:
        result = await client.search_notes(query, limit)
        notes = result.get('data', [])
        
        output = f"🔍 Note Search Results\n{'=' * 60}\n"
        output += f"Query: '{query}'\n"
        output += f"Found: {len(notes)} notes\n\n"
        
        if notes:
            for i, note in enumerate(notes, 1):
                output += f"{i}. {note.get('message', 'No message')}\n"
                output += f"   Session: {note.get('sessionId', 'Unknown')}\n"
                output += f"   By: {note.get('userName', 'Unknown')}\n"
                
                if note.get('createdAt'):
                    dt = datetime.fromtimestamp(note['createdAt'] / 1000)
                    output += f"   Date: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
                
                if note.get('tag'):
                    output += f"   Tag: {note['tag']}\n"
                output += "\n"
        else:
            output += f"No notes found matching '{query}'."
        
        return output
        
    except Exception as e:
        return f"Error searching notes: {str(e)}"


# ============================================================================
# Server Lifecycle
# ============================================================================

# Run the server
if __name__ == "__main__":
    mcp.run()