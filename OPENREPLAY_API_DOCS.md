# OpenReplay Session Analysis API Documentation

## Overview
This document provides comprehensive API documentation for building an MCP server that can analyze OpenReplay sessions, based on analysis of the OpenReplay codebase.

## Base Configuration

### Authentication
- **API Key**: Organization API key (found in Preferences > Account > Organization API Key)
- **Base URL**: `https://api.openreplay.com`
- **Headers**: 
  ```json
  {
    "Authorization": "YOUR_API_KEY",
    "Content-Type": "application/json"
  }
  ```

## Core Session APIs

### 1. Search Sessions
**POST** `/api/v1/{projectId}/sessions/search`

Search and filter sessions with advanced criteria.

**Request Body:**
```json
{
  "startTimestamp": 1234567890000,  // Unix timestamp in ms
  "endTimestamp": 1234567890000,
  "limit": 50,
  "page": 1,
  "sort": "startTs",  // Options: startTs, duration, eventsCount, errorsCount
  "order": "DESC",     // Options: DESC, ASC
  "filters": [
    {
      "is_event": false,
      "type": "USERID",  // FilterType enum
      "operator": "is",
      "value": ["user123"]
    }
  ],
  "events": [],  // Event filters
  "group_by_user": false,
  "bookmarked": false
}
```

**Response:**
```json
{
  "data": {
    "total": 100,
    "sessions": [
      {
        "projectId": 123,
        "sessionId": "3448097416140724967",
        "userUuid": "96427ccd-d6e3-4f44-887e-af78fad187c1",
        "userId": "user123",
        "userOs": "Mac OS X",
        "userBrowser": "Safari",
        "userDevice": "",
        "userCountry": "US",
        "userCity": "San Francisco",
        "userState": "CA",
        "startTs": 1234567890000,
        "duration": 913300,  // ms
        "eventsCount": 6,
        "pagesCount": 4,
        "errorsCount": 0,
        "platform": "web",
        "issueScore": 0,
        "issueTypes": [],
        "viewed": false,
        "favorite": false
      }
    ]
  }
}
```

### 2. Get Session Replay Data
**GET** `/api/v1/{projectId}/sessions/{sessionId}/replay`

Get complete session replay data including DOM mutations and events.

**Response:**
```json
{
  "data": {
    "session": {
      "sessionId": "123456",
      "duration": 60000,
      "startTs": 1234567890000,
      "events": [...]
    },
    "events": [...],  // Replay events
    "dom": [...],      // DOM mutations
    "resources": [...],
    "errors": [],
    "network": []
  }
}
```

### 3. Get Session Events
**GET** `/api/v1/{projectId}/sessions/{sessionId}/events`

Get high-level events for a session.

**Response:**
```json
{
  "data": [
    {
      "type": "click",
      "timestamp": 1234567890000,
      "element": "button#submit",
      "url": "/checkout"
    }
  ]
}
```

### 4. Get User Sessions
**GET** `/api/v1/{projectId}/users/{userId}/sessions`

Get all sessions for a specific user.

**Response:**
```json
{
  "data": [
    {
      "sessionId": "3448097416140724967",
      "duration": 913300,
      "startTs": 1234567890000,
      "pagesCount": 4,
      "eventsCount": 6,
      "errorsCount": 0
    }
  ]
}
```

### 5. Get User Statistics
**GET** `/api/v1/{projectId}/users/{userId}`

Get user statistics and information.

**Response:**
```json
{
  "data": {
    "userId": "user123",
    "sessionCount": 42,
    "firstSeen": 1234567890000,
    "lastSeen": 1234567890000
  }
}
```

## Live Session APIs (Assist)

### 1. Get Live Sessions
**POST** `/api/v1/{projectId}/assist/sessions`

Get currently active live sessions.

**Request Body:**
```json
{
  "filters": [
    {
      "type": "USERID",
      "value": "user123",
      "operator": "contains"
    }
  ],
  "sort": "TIMESTAMP",
  "order": "DESC",
  "limit": 50,
  "page": 1
}
```

**Response:**
```json
{
  "data": {
    "total": 5,
    "sessions": [
      {
        "sessionId": "live_123",
        "userId": "user123",
        "userBrowser": "Chrome",
        "userOs": "Windows",
        "live": true,
        "projectId": 123,
        "startTs": 1234567890000,
        "activeTab": true,
        "metadata": {}
      }
    ]
  }
}
```

### 2. Get Live Session Details
**GET** `/api/v1/{projectId}/assist/sessions/{sessionId}`

Get details for a specific live session.

## Session Notes

### 1. Create Session Note
**POST** `/api/v1/{projectId}/sessions/{sessionId}/notes`

**Request Body:**
```json
{
  "message": "User encountered checkout issue",
  "timestamp": 1234567890000,
  "is_public": false,
  "tag": "bug"
}
```

### 2. Get Session Notes
**GET** `/api/v1/{projectId}/sessions/{sessionId}/notes`

## Error Analysis

### 1. Get Error Details
**GET** `/api/v1/{projectId}/errors/{errorId}`

### 2. Get Error Sessions
**GET** `/api/v1/{projectId}/errors/{errorId}/sessions`

## Filter Types and Enums

### FilterType Enum
```python
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
```

### EventType Enum
```python
CLICK = "click"
INPUT = "input"
LOCATION = "location"
CUSTOM = "custom"
ERROR = "error"
```

### SearchEventOperator Enum
```python
IS = "is"
IS_NOT = "isNot"
CONTAINS = "contains"
NOT_CONTAINS = "notContains"
STARTS_WITH = "startsWith"
ENDS_WITH = "endsWith"
```

## Python Implementation Example

```python
import httpx
import asyncio
from typing import Dict, List, Optional

class OpenReplayAPI:
    def __init__(self, api_key: str, project_id: str):
        self.api_key = api_key
        self.project_id = project_id
        self.base_url = "https://api.openreplay.com"
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
    
    async def search_sessions(self, 
                            user_id: Optional[str] = None,
                            start_timestamp: Optional[int] = None,
                            end_timestamp: Optional[int] = None,
                            limit: int = 50) -> Dict:
        """Search sessions with filters"""
        
        filters = []
        if user_id:
            filters.append({
                "is_event": False,
                "type": "userId",
                "operator": "is",
                "value": [user_id]
            })
        
        payload = {
            "filters": filters,
            "limit": limit,
            "page": 1,
            "sort": "startTs",
            "order": "DESC"
        }
        
        if start_timestamp:
            payload["startTimestamp"] = start_timestamp
        if end_timestamp:
            payload["endTimestamp"] = end_timestamp
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/{self.project_id}/sessions/search",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    async def get_user_sessions(self, user_id: str) -> Dict:
        """Get all sessions for a user"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/{self.project_id}/users/{user_id}/sessions",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_session_replay(self, session_id: str) -> Dict:
        """Get complete session replay data"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/{self.project_id}/sessions/{session_id}/replay",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_session_events(self, session_id: str) -> Dict:
        """Get session events"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/{self.project_id}/sessions/{session_id}/events",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_live_sessions(self, user_id: Optional[str] = None) -> Dict:
        """Get live sessions"""
        filters = []
        if user_id:
            filters.append({
                "type": "userId",
                "value": user_id,
                "operator": "contains"
            })
        
        payload = {
            "filters": filters,
            "sort": "TIMESTAMP",
            "order": "DESC",
            "limit": 50,
            "page": 1
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/{self.project_id}/assist/sessions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()

# Usage Example
async def main():
    api = OpenReplayAPI(
        api_key="YOUR_API_KEY",
        project_id="YOUR_PROJECT_ID"
    )
    
    # Search sessions for a user
    sessions = await api.search_sessions(user_id="user123")
    print(f"Found {sessions['data']['total']} sessions")
    
    # Get session replay data
    if sessions['data']['sessions']:
        session_id = sessions['data']['sessions'][0]['sessionId']
        replay = await api.get_session_replay(session_id)
        print(f"Session {session_id} has {len(replay['data']['events'])} events")

if __name__ == "__main__":
    asyncio.run(main())
```

## Notes

1. The API uses pagination - use `page` and `limit` parameters
2. Timestamps are in Unix milliseconds
3. The assist endpoints require special configuration on the server side
4. Some endpoints may require additional permissions
5. Rate limiting may apply - handle 429 status codes appropriately