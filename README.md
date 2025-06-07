# OpenReplay Session Analysis MCP Server

A Model Context Protocol (MCP) server for analyzing OpenReplay session recordings and user behavior patterns. This server enables AI assistants to analyze user sessions, detect problems, and provide actionable insights from OpenReplay data.

## 🔥 Features

- 🔍 **Session Search & Filtering** - Find sessions by date, user, errors, duration
- 📊 **User Journey Analysis** - Track page flows and navigation patterns  
- 🐛 **Problem Detection** - Identify rage clicks, form abandonment, errors
- 🤖 **AI-Powered Insights** - Generate intelligent session summaries
- 👥 **User Behavior Analysis** - Analyze patterns across multiple sessions
- 🔗 **Similar Session Finding** - Discover sessions with comparable issues

## 🚀 Quick Start

1. **Clone and setup:**
   ```bash
   git clone https://github.com/rsp2k/openreplay-mcp-server.git
   cd openreplay-mcp-server
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure OpenReplay credentials:**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenReplay API credentials
   ```

3. **Run the server:**
   ```bash
   python run_server.py
   ```

## ⚙️ Configuration

Set these environment variables in your `.env` file:

```env
OPENREPLAY_API_URL=https://api.openreplay.com
OPENREPLAY_API_KEY=your_api_key_here
OPENREPLAY_PROJECT_ID=your_project_id_here
```

To get your OpenReplay API credentials:
1. Go to your OpenReplay dashboard
2. Navigate to Settings → API Keys
3. Generate a new API key
4. Copy your Project ID from the URL or project settings

## 🛠️ Available Tools

### Session Management
- `search_sessions` - Search sessions with advanced filters
- `get_session_details` - Get detailed session information
- `get_user_session_history` - View all sessions for a specific user

### Analysis Tools  
- `analyze_user_journey` - Map user navigation patterns and page flows
- `detect_problem_patterns` - Find rage clicks, form issues, and errors
- `generate_session_summary` - AI-powered session insights and recommendations
- `find_similar_sessions` - Discover related problematic sessions

## 📋 Usage with Claude Desktop

Add to your Claude Desktop MCP configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "openreplay-analysis": {
      "command": "python",
      "args": ["/path/to/openreplay-mcp-server/run_server.py"],
      "env": {
        "OPENREPLAY_API_KEY": "your_api_key_here",
        "OPENREPLAY_PROJECT_ID": "your_project_id_here"
      }
    }
  }
}
```

## 💬 Example Queries

Once connected to Claude Desktop or another MCP client, you can ask:

- *"Find sessions with errors from the last week"*
- *"Analyze user journey for session ABC123"*
- *"Generate a summary of problematic sessions today"*
- *"Show me all sessions for user john@example.com"*
- *"Find sessions similar to XYZ456 that had form abandonment"*
- *"Debug session DEF789 and tell me what went wrong"*

## 🐳 Docker Usage

For containerized deployment:

```bash
# Set environment variables in .env file
docker-compose up
```

Or build and run manually:

```bash
docker build -t openreplay-mcp .
docker run -e OPENREPLAY_API_KEY=your_key -e OPENREPLAY_PROJECT_ID=your_project openreplay-mcp
```

## 🔧 Development

The server is built with:
- **FastMCP** - Official Python MCP SDK for server implementation
- **httpx** - Async HTTP client for OpenReplay API
- **asyncio** - Async/await support

### Project Structure

```
openreplay-mcp-server/
├── openreplay_session_analyzer.py  # OpenReplay client and analysis logic
├── run_server.py                   # FastMCP server with tools
├── mcp.py                          # Django MCP configuration (optional)
├── settings.py                     # Django settings (optional)
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── Dockerfile                      # Container configuration
├── docker-compose.yml              # Docker Compose setup
└── README.md                       # This file
```

### Adding New Analysis Features

1. Add new methods to the `SessionAnalyzer` class in `openreplay_session_analyzer.py`
2. Create corresponding `@mcp.tool()` decorated functions in `run_server.py`
3. Test with your OpenReplay data

## 📊 Session Analysis Capabilities

### Problem Detection
- **Rage Clicks**: Multiple rapid clicks indicating frustration
- **Form Abandonment**: Users starting but not completing forms
- **Dead Clicks**: Clicks on non-interactive elements
- **Error Tracking**: JavaScript errors and exceptions

### Journey Analysis
- **Page Flow Mapping**: Track user navigation through your site
- **Duration Analysis**: Understand time spent on each page
- **Bounce Rate**: Identify single-page sessions
- **Action Breakdown**: Analyze user interactions (clicks, scrolls, inputs)

### AI Insights
- **Automated Summaries**: Natural language session descriptions
- **Problem Identification**: Highlight potential UX issues
- **Performance Analysis**: Identify slow-loading content
- **Behavioral Patterns**: Recognize user intent and goals

## 🔗 Integration Examples

### Debugging Workflow
```python
# Search for recent error sessions
sessions = await search_sessions(has_errors=True, start_date="2024-06-01")

# Analyze specific problematic session
summary = await generate_session_summary(session_id="abc123")
problems = await detect_problem_patterns(session_id="abc123")

# Find similar issues
similar = await find_similar_sessions(reference_session_id="abc123", criteria="errors")
```

### UX Research Workflow
```python
# Analyze user behavior over time
user_history = await get_user_session_history(user_id="user123")

# Study navigation patterns
for session in user_sessions:
    journey = await analyze_user_journey(session_id=session.id)
    # Analyze patterns...
```

## 📝 API Requirements

This server requires:
- OpenReplay account with API access
- Valid API key and project ID
- Network access to OpenReplay API endpoints
- Python 3.8+ environment

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenReplay](https://openreplay.com/) for providing the session replay platform
- [Model Context Protocol](https://github.com/modelcontextprotocol/python-sdk) for the integration framework
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) for the Python MCP SDK

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/rsp2k/openreplay-mcp-server/issues) page
2. Create a new issue with detailed information
3. Join the discussion in existing issues

---

**Built with ❤️ for better user experience analysis**
