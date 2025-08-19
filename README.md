# OpenReplay MCP Server

A comprehensive Model Context Protocol (MCP) server for analyzing OpenReplay session data, monitoring live sessions, and generating actionable insights.

## 🚀 Features

- **Session Analysis**: Deep analysis of user sessions with AI-powered insights
- **Live Monitoring**: Real-time monitoring of active user sessions
- **User Behavior Analysis**: Comprehensive user journey and engagement metrics
- **Pattern Detection**: Automatic detection of user behavior patterns
- **Error Tracking**: Monitor and analyze session errors
- **Event Timeline**: Detailed session event analysis and timeline
- **Geographic Analytics**: User distribution and location insights
- **Browser/Device Analytics**: Technical usage patterns

## 📋 Requirements

- Python 3.8+
- OpenReplay API access
- Valid API key and project ID

## 🔧 Installation

### Option 1: Direct Installation
```bash
pip install -r requirements.txt
```

### Option 2: Development Installation
```bash
git clone <repository-url>
cd openreplay-mcp-server
pip install -e .
```

## ⚙️ Configuration

Set the following environment variables:

```bash
export OPENREPLAY_API_KEY="your_api_key_here"
export OPENREPLAY_PROJECT_ID="your_project_id_here"
export OPENREPLAY_API_URL="https://api.openreplay.com"  # Optional, defaults to public API
```

### Getting Your Credentials

1. **API Key**: Go to OpenReplay Dashboard → Preferences → Account → Organization API Key
2. **Project ID**: Found in your project settings or URL

## 🚀 Usage

### Running the MCP Server

```bash
python openreplay_mcp_working.py
```

### Available MCP Tools

1. **`analyze_user_sessions(user_id, days_back=7)`**
   - Comprehensive analysis of a user's session history
   - Generates insights and behavior patterns
   - Tracks engagement metrics and technical details

2. **`get_session_details(session_id)`**
   - Detailed analysis of a specific session
   - Event timeline and user journey
   - Error detection and interaction analysis

3. **`monitor_live_sessions()`**
   - Real-time monitoring of active sessions
   - Browser and geographic distribution
   - Activity status tracking

4. **`get_project_overview()`**
   - Project information and statistics
   - Organization overview
   - API status and configuration

## 📊 Example Output

### User Analysis
```
👤 User Analysis: user123
================================================================================

📊 User Overview:
• Total Sessions: 15
• Sessions Analyzed: 8
• User Lifetime: 23 days

📈 Engagement Analysis:
• Avg Session Duration: 8.3 minutes
• Avg Pages per Session: 5.2
• Error Rate: 2.1%

💡 AI Insights:
⏰ Long engagement sessions (8.3 min avg) - good retention
📱 Mobile-first usage (67% mobile)
✅ Low error rate (2.1%) - stable experience

📋 Recent Sessions:
1. Session 1234567890
   Duration: 12.5 min | Pages: 8 | Errors: 0
   Browser: Chrome on iOS
```

### Live Session Monitoring
```
🔴 Live Session Monitor
================================================================================
Active Sessions: 12

📊 Session Status:
• Active Tabs: 8
• Background Tabs: 4

🖥️ Browser Distribution:
• Chrome: 7 sessions
• Safari: 3 sessions
• Firefox: 2 sessions

👥 Active Users:
1. User: alice@example.com
   Browser: Chrome on macOS
   Duration: 5.2 min
   Status: 🟢 Active
```

## 🔧 API Endpoints Used

The server uses the following OpenReplay API endpoints:

- `GET /api/v1/{project}/users/{user_id}/sessions` - User sessions
- `GET /api/v1/{project}/users/{user_id}` - User statistics  
- `GET /api/v1/{project}/sessions/{session_id}/events` - Session events
- `POST /api/v1/{project}/assist/sessions` - Live sessions
- `GET /api/v1/projects` - Project list
- `GET /api/v1/projects/{project_id}` - Project details

## 🐛 Troubleshooting

### Common Issues

1. **404 Errors**: Some endpoints are only available in self-hosted OpenReplay instances
2. **Authentication**: Ensure your API key has proper permissions
3. **Rate Limiting**: The API may have rate limits - implement retry logic if needed

### Debug Mode

Set environment variable for detailed logging:
```bash
export OPENREPLAY_DEBUG=true
```

## 📝 License

MIT License - see LICENSE file for details.

## 🆘 Support

- Check the [OpenReplay Documentation](https://docs.openreplay.com)
- File issues on GitHub
- Join the OpenReplay community

## ⚡ Performance Notes

- The server caches frequently accessed data
- Use appropriate `days_back` limits for large datasets
- Live session monitoring has minimal performance impact
- Session analysis scales with the number of events per session

## 🔐 Security

- Never commit API keys to version control
- Use environment variables for all sensitive configuration
- The server only reads data - no write operations to OpenReplay
- All API communication is over HTTPS