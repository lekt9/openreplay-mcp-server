"""
OpenReplay MCP Server - Working Implementation
Focused on endpoints that actually work with the public API
"""

import os
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

import httpx
from fastmcp import FastMCP, Context


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class OpenReplayConfig:
    """OpenReplay API configuration"""
    api_url: str = os.getenv('OPENREPLAY_API_URL', 'https://api.openreplay.com')
    api_key: str = os.getenv('OPENREPLAY_API_KEY', '')
    project_id: str = os.getenv('OPENREPLAY_PROJECT_KEY', os.getenv('OPENREPLAY_PROJECT_ID', ''))


# ============================================================================
# API Client - Working Endpoints Only
# ============================================================================

class OpenReplayClient:
    """OpenReplay API client with verified working endpoints"""
    
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
    
    async def get_user_sessions(self, user_id: str,
                               start_date: Optional[int] = None,
                               end_date: Optional[int] = None) -> Dict:
        """Get all sessions for a specific user - WORKING"""
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
        """Get statistics for a specific user - WORKING"""
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/users/{user_id}"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_session_events(self, session_id: str) -> Dict:
        """Get high-level events for a session - WORKING"""
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/{self.config.project_id}/sessions/{session_id}/events"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_live_sessions(self, filters: List[Dict] = None,
                               sort: str = "TIMESTAMP",
                               order: str = "DESC",
                               limit: int = 50,
                               page: int = 1) -> Dict:
        """Get currently active live sessions - WORKING"""
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
    
    async def get_projects(self) -> Dict:
        """Get list of all projects - WORKING"""
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/projects"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_project_details(self, project_id: str = None) -> Dict:
        """Get details for a specific project - WORKING"""
        pid = project_id or self.config.project_id
        response = await self.client.get(
            f"{self.config.api_url}/api/v1/projects/{pid}"
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
    """Session analysis engine for working with available data"""
    
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
            
            # Time patterns
            if session.get('startTs'):
                hour = datetime.fromtimestamp(session['startTs'] / 1000).hour
                hourly_distribution[hour] += 1
        
        # Calculate metrics
        num_sessions = len(sessions)
        
        # User metrics
        patterns['user_metrics'] = {
            'unique_users': len(set(s.get('userId', s.get('userUuid', '')) for s in sessions)),
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
            'high_engagement_sessions': sum(1 for s in sessions if s.get('duration', 0) > 300000),  # > 5 minutes
            'error_rate': (sessions_with_errors / num_sessions * 100) if num_sessions > 0 else 0,
            'sessions_with_errors': sessions_with_errors
        }
        
        # Time patterns
        patterns['time_patterns'] = {
            'hourly_distribution': hourly_distribution,
            'peak_hours': sorted(enumerate(hourly_distribution), key=lambda x: x[1], reverse=True)[:3]
        }
        
        return patterns
    
    @staticmethod
    def generate_insights(patterns: Dict) -> List[str]:
        """Generate actionable insights from patterns"""
        insights = []
        
        # Engagement insights
        engagement = patterns.get('engagement_metrics', {})
        avg_duration_min = engagement.get('avg_duration', 0) / 60000
        
        if avg_duration_min < 1:
            insights.append(f"⚡ Very short sessions ({avg_duration_min:.1f} min avg) - users leaving quickly")
        elif avg_duration_min > 10:
            insights.append(f"⏰ Long engagement sessions ({avg_duration_min:.1f} min avg) - good retention")
        
        bounce_rate = engagement.get('bounce_rate', 0)
        if bounce_rate > 70:
            insights.append(f"🔴 High bounce rate ({bounce_rate:.1f}%) - landing page needs improvement")
        elif bounce_rate < 30:
            insights.append(f"✅ Excellent bounce rate ({bounce_rate:.1f}%) - users exploring site")
        
        error_rate = engagement.get('error_rate', 0)
        if error_rate > 50:
            insights.append(f"🚨 Critical: {error_rate:.1f}% of sessions have errors")
        elif error_rate > 20:
            insights.append(f"⚠️ {error_rate:.1f}% error rate needs attention")
        elif error_rate > 0:
            insights.append(f"ℹ️ {error_rate:.1f}% error rate - monitor trends")
        else:
            insights.append("✅ No errors detected - stable experience")
        
        # Technical insights
        tech = patterns.get('technical_metrics', {})
        mobile_pct = tech.get('mobile_percentage', 0)
        if mobile_pct > 50:
            insights.append(f"📱 Mobile-first usage ({mobile_pct:.1f}% mobile)")
        elif mobile_pct < 20:
            insights.append(f"💻 Desktop-dominated usage ({100-mobile_pct:.1f}% desktop)")
        
        # Browser insights
        browsers = tech.get('browsers', {})
        if browsers:
            top_browser = max(browsers, key=browsers.get)
            browser_pct = (browsers[top_browser] / sum(browsers.values()) * 100)
            insights.append(f"📊 {top_browser} dominates ({browser_pct:.1f}% of sessions)")
        
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


@mcp.tool()
async def analyze_user_sessions(
    user_id: str,
    days_back: int = 7
) -> str:
    """
    Analyze all sessions for a specific user with comprehensive insights.
    
    Args:
        user_id: The user ID to analyze
        days_back: Number of days to look back for analysis
    
    Returns:
        Comprehensive user session analysis with patterns and insights
    """
    try:
        # Get user stats and sessions
        user_stats = await client.get_user_stats(user_id)
        user_sessions = await client.get_user_sessions(user_id)
        
        user_data = user_stats.get('data', {})
        sessions = user_sessions.get('data', [])
        
        # Filter sessions by date if specified
        if days_back and sessions:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            cutoff_timestamp = int(cutoff_date.timestamp() * 1000)
            sessions = [s for s in sessions if s.get('startTs', 0) > cutoff_timestamp]
        
        output = f"👤 User Analysis: {user_id}\n"
        output += f"{'=' * 80}\n\n"
        
        # User statistics
        output += f"📊 User Overview:\n"
        output += f"• Total Sessions: {user_data.get('sessionCount', 0)}\n"
        output += f"• Sessions Analyzed: {len(sessions)} (last {days_back} days)\n"
        
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
            # Analyze patterns
            patterns = analyzer.analyze_session_patterns(sessions)
            insights = analyzer.generate_insights(patterns)
            
            # Engagement metrics
            engagement = patterns.get('engagement_metrics', {})
            output += f"📈 Engagement Analysis:\n"
            output += f"• Avg Session Duration: {engagement.get('avg_duration', 0)/60000:.1f} minutes\n"
            output += f"• Avg Pages per Session: {engagement.get('avg_pages', 0):.1f}\n"
            output += f"• Avg Events per Session: {engagement.get('avg_events', 0):.1f}\n"
            output += f"• Bounce Rate: {engagement.get('bounce_rate', 0):.1f}%\n"
            output += f"• Error Rate: {engagement.get('error_rate', 0):.1f}%\n\n"
            
            # Technical breakdown
            tech = patterns.get('technical_metrics', {})
            if tech.get('browsers'):
                output += f"🖥️ Browser Usage:\n"
                for browser, count in tech['browsers'].items():
                    pct = (count / len(sessions) * 100)
                    output += f"• {browser}: {count} sessions ({pct:.1f}%)\n"
                output += "\n"
            
            # Geographic distribution
            user_metrics = patterns.get('user_metrics', {})
            if user_metrics.get('geographic_distribution'):
                output += f"🌍 Geographic Distribution:\n"
                for country, count in user_metrics['top_countries']:
                    pct = (count / len(sessions) * 100)
                    output += f"• {country}: {count} sessions ({pct:.1f}%)\n"
                output += "\n"
            
            # AI Insights
            if insights:
                output += f"💡 AI Insights:\n"
                for insight in insights:
                    output += f"{insight}\n"
                output += "\n"
            
            # Recent sessions
            output += f"📋 Recent Sessions:\n"
            recent_sessions = sorted(sessions, key=lambda x: x.get('startTs', 0), reverse=True)
            for i, session in enumerate(recent_sessions[:5], 1):
                output += f"\n{i}. Session {session.get('sessionId', 'Unknown')}\n"
                output += f"   Duration: {session.get('duration', 0)/60000:.1f} min | "
                output += f"Pages: {session.get('pagesCount', 0)} | "
                output += f"Events: {session.get('eventsCount', 0)} | "
                output += f"Errors: {session.get('errorsCount', 0)}\n"
                
                if session.get('startTs'):
                    dt = datetime.fromtimestamp(session['startTs'] / 1000)
                    output += f"   Date: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    
                output += f"   Browser: {session.get('userBrowser', 'Unknown')} on {session.get('userOs', 'Unknown')}\n"
                output += f"   Location: {session.get('userCountry', 'Unknown')}\n"
        else:
            output += "No sessions found for the specified time period."
        
        return output
        
    except Exception as e:
        return f"Error analyzing user sessions: {str(e)}"


@mcp.tool()
async def get_session_details(session_id: str) -> str:
    """
    Get detailed analysis of a specific session including events and timeline.
    
    Args:
        session_id: The session ID to analyze
    
    Returns:
        Detailed session analysis with events timeline
    """
    try:
        # Get session events
        events_result = await client.get_session_events(session_id)
        events = events_result.get('data', [])
        
        output = f"🎬 Session Analysis: {session_id}\n"
        output += f"{'=' * 80}\n\n"
        
        if events:
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
            
            output += f"📊 Event Summary ({len(events)} total events):\n"
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
                    if error.get('source'):
                        output += f"   Source: {error['source']}\n"
                output += "\n"
            
            # Timeline view
            output += f"⏱️ Event Timeline (First 10 events):\n"
            sorted_events = sorted(events, key=lambda x: x.get('timestamp', 0))
            for i, event in enumerate(sorted_events[:10], 1):
                timestamp = event.get('timestamp', 0)
                time_str = f"{timestamp/1000:.1f}s"
                output += f"{i}. [{time_str}] {event.get('type', 'unknown')}"
                
                if event.get('url'):
                    output += f" at {event['url']}"
                elif event.get('element'):
                    output += f" on {event['element']}"
                elif event.get('message'):
                    output += f" - {event['message'][:50]}..."
                
                output += "\n"
        else:
            output += "No events found for this session."
        
        return output
        
    except Exception as e:
        return f"Error analyzing session: {str(e)}"


@mcp.tool()
async def monitor_live_sessions() -> str:
    """
    Monitor currently active live sessions and their status.
    
    Returns:
        Real-time overview of active sessions
    """
    try:
        result = await client.get_live_sessions()
        sessions = result.get('data', {}).get('sessions', [])
        total = result.get('data', {}).get('total', 0)
        
        output = f"🔴 Live Session Monitor\n"
        output += f"{'=' * 80}\n\n"
        output += f"Active Sessions: {total}\n\n"
        
        if sessions:
            # Activity status
            active_tabs = sum(1 for s in sessions if s.get('activeTab'))
            output += f"📊 Session Status:\n"
            output += f"• Active Tabs: {active_tabs}\n"
            output += f"• Background Tabs: {total - active_tabs}\n\n"
            
            # Group by browser and country
            browsers = {}
            countries = {}
            for session in sessions:
                browser = session.get('userBrowser', 'Unknown')
                browsers[browser] = browsers.get(browser, 0) + 1
                
                country = session.get('userCountry', 'Unknown')
                countries[country] = countries.get(country, 0) + 1
            
            output += f"🖥️ Browser Distribution:\n"
            for browser, count in sorted(browsers.items(), key=lambda x: x[1], reverse=True):
                output += f"• {browser}: {count} sessions\n"
            output += "\n"
            
            if len(countries) > 1:
                output += f"🌍 Geographic Distribution:\n"
                for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]:
                    output += f"• {country}: {count} sessions\n"
                output += "\n"
            
            # Individual sessions
            output += f"👥 Active Users:\n"
            for i, session in enumerate(sessions[:10], 1):
                output += f"\n{i}. User: {session.get('userId', 'Anonymous')}\n"
                output += f"   Session: {session['sessionId']}\n"
                output += f"   Browser: {session.get('userBrowser', 'Unknown')} on {session.get('userOs', 'Unknown')}\n"
                output += f"   Location: {session.get('userCountry', 'Unknown')}\n"
                
                if session.get('startTs'):
                    duration = (datetime.now().timestamp() * 1000 - session['startTs']) / 60000
                    output += f"   Duration: {duration:.1f} min\n"
                
                status = '🟢 Active' if session.get('activeTab') else '🟡 Background'
                output += f"   Status: {status}\n"
                
                if session.get('metadata'):
                    metadata_str = ', '.join(f"{k}: {v}" for k, v in session.get('metadata', {}).items())
                    if metadata_str:
                        output += f"   Metadata: {metadata_str}\n"
        else:
            output += "No active sessions at the moment."
        
        return output
        
    except Exception as e:
        return f"Error monitoring live sessions: {str(e)}"


@mcp.tool()
async def get_project_overview() -> str:
    """
    Get overview of the current OpenReplay project and available data.
    
    Returns:
        Project statistics and data availability
    """
    try:
        # Get project details
        project_result = await client.get_project_details()
        project_data = project_result.get('data', {})
        
        output = f"📁 Project Overview\n"
        output += f"{'=' * 80}\n\n"
        
        output += f"📊 Project Information:\n"
        output += f"• Project ID: {project_data.get('projectId', 'Unknown')}\n"
        output += f"• Project Key: {project_data.get('projectKey', 'Unknown')}\n"
        output += f"• Name: {project_data.get('name', 'Unknown')}\n"
        output += f"• Platform: {project_data.get('platform', 'Unknown')}\n\n"
        
        # Get all projects for context
        projects_result = await client.get_projects()
        all_projects = projects_result.get('data', [])
        
        output += f"🏢 Organization Projects ({len(all_projects)} total):\n"
        for project in all_projects:
            status = "📍 Current" if str(project.get('projectId')) == config.project_id else "  "
            output += f"{status} {project.get('name', 'Unknown')} ({project.get('platform', 'unknown')})\n"
        output += "\n"
        
        # Get live sessions for activity check
        live_result = await client.get_live_sessions()
        live_sessions = live_result.get('data', {}).get('sessions', [])
        
        output += f"🔴 Current Activity:\n"
        output += f"• Live Sessions: {len(live_sessions)}\n"
        
        if live_sessions:
            active_users = len(set(s.get('userId', 'anon') for s in live_sessions))
            output += f"• Active Users: {active_users}\n"
            
            browsers = {}
            for session in live_sessions:
                browser = session.get('userBrowser', 'Unknown')
                browsers[browser] = browsers.get(browser, 0) + 1
            
            if browsers:
                top_browser = max(browsers, key=browsers.get)
                output += f"• Top Browser: {top_browser} ({browsers[top_browser]} sessions)\n"
        
        output += "\n"
        
        # API status
        output += f"🔧 API Status:\n"
        output += f"• Base URL: {config.api_url}\n"
        output += f"• API Key: {'✅ Set' if config.api_key else '❌ Missing'}\n"
        output += f"• Project ID: {'✅ Set' if config.project_id else '❌ Missing'}\n"
        
        return output
        
    except Exception as e:
        return f"Error getting project overview: {str(e)}"


# Run the server
if __name__ == "__main__":
    mcp.run()