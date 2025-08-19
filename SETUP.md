# OpenReplay MCP Server Setup Guide

## Configuration

1. **Create a `.env` file** in the project root with your OpenReplay credentials:

```bash
# OpenReplay Configuration
# For cloud: https://app.openreplay.com
# For self-hosted: https://your-domain.com
OPENREPLAY_API_URL=https://app.openreplay.com

# Your API key from OpenReplay dashboard
# Found in: Preferences > Account > Organization API Key
OPENREPLAY_API_KEY=your_api_key_here

# Your project ID from OpenReplay
# Found in: Preferences > Projects
OPENREPLAY_PROJECT_ID=your_project_id_here
```

2. **Get your API Key**:
   - Log into your OpenReplay dashboard
   - Go to **Preferences** > **Account** > **Organization API Key**
   - Copy the API key

3. **Get your Project ID**:
   - Go to **Preferences** > **Projects**
   - Copy the Project ID (looks like: `34vlVhQDDp5g4jhtL15M`)

## API Endpoints (Official OpenReplay API)

The server uses the official OpenReplay API endpoints:

- **List Projects**: `GET /api/v1/projects`
- **User Sessions**: `GET /api/v1/{projectKey}/users/{userId}/sessions`
- **User Stats**: `GET /api/v1/{projectKey}/users/{userId}`
- **Session Events**: `GET /api/v1/{projectKey}/sessions/{sessionId}/events`

**Important**: The OpenReplay API requires a user ID to fetch sessions. You need to know the user IDs from your application (set via `tracker.setUserID()`).

## Common Issues

### 404 Not Found Error
If you get a 404 error, check:
1. Your `OPENREPLAY_API_URL` - should be `https://app.openreplay.com` for cloud or your self-hosted URL
2. Your `OPENREPLAY_PROJECT_ID` is correct
3. Your API key has the necessary permissions

### Authentication Error
If you get a 401/403 error:
1. Verify your API key is correct
2. Check that the API key has access to the project
3. Ensure the API key hasn't expired

## Testing the Connection

Run the server and test with a simple session search:
```bash
uv run python run_server.py
```

The server should start and be ready to accept MCP requests.