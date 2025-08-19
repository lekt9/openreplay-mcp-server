#!/usr/bin/env python3
"""Test the MCP tool functionality"""

import asyncio
import os

# Set environment variables
os.environ['OPENREPLAY_API_KEY'] = '5auNKdVzDfvUTjsBEDbf'
os.environ['OPENREPLAY_PROJECT_ID'] = '34vlVhQDDp5g4jhtL15M'

# Import after setting env vars
from openreplay_session_analyzer import OpenReplaySessionAnalysisTools

async def test_mcp_tool():
    tools = OpenReplaySessionAnalysisTools()
    
    try:
        print("Testing MCP Tool: get_user_session_history")
        print("=" * 60)
        
        result = await tools.get_user_session_history(
            user_id='k9742x5h3jbxjx20k52b2dt6th7ng54e',
            limit=5
        )
        
        print(result)
        
    finally:
        # Clean up
        await tools.client.close()

if __name__ == "__main__":
    asyncio.run(test_mcp_tool())