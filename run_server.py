"""
Standalone script to run the OpenReplay MCP Server
"""
import os
import sys
import asyncio
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openreplay_mcp.settings')

import django
django.setup()

from openreplay_session_analyzer import server, config

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
    
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)