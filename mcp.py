"""
OpenReplay MCP Tools - mcp.py
This file defines the MCP toolsets for django-mcp-server
"""

from openreplay_session_analyzer import OpenReplaySessionAnalysisTools

# Create an instance of the tools that will be discovered by django-mcp-server
openreplay_analysis = OpenReplaySessionAnalysisTools()
