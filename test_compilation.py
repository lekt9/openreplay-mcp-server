#!/usr/bin/env python3
"""Test compilation and imports"""

import os
import sys

# Set environment variables first
os.environ['OPENREPLAY_API_KEY'] = '5auNKdVzDfvUTjsBEDbf'
os.environ['OPENREPLAY_PROJECT_ID'] = '34vlVhQDDp5g4jhtL15M'

print("Testing imports and compilation...")

try:
    print("1. Testing basic imports...")
    import httpx
    import asyncio
    from datetime import datetime, timedelta
    from typing import List, Dict, Any, Optional, Union
    from dataclasses import dataclass
    from enum import Enum
    print("   ✅ Basic imports successful")
    
    print("2. Testing FastMCP import...")
    from fastmcp import FastMCP, Context
    print("   ✅ FastMCP import successful")
    
    print("3. Testing Pydantic import...")
    from pydantic import BaseModel, Field
    print("   ✅ Pydantic import successful")
    
    print("4. Testing main module import...")
    try:
        import openreplay_mcp_server
        print("   ✅ Main module import successful")
        
        # Test configuration
        print("5. Testing configuration...")
        config = openreplay_mcp_server.OpenReplayConfig()
        print(f"   API URL: {config.api_url}")
        print(f"   Project ID: {config.project_id[:10]}...")
        print(f"   API Key: {'***' + config.api_key[-4:] if config.api_key else 'NOT SET'}")
        print("   ✅ Configuration successful")
        
        # Test client instantiation
        print("6. Testing client instantiation...")
        client = openreplay_mcp_server.OpenReplayClient(config)
        print("   ✅ Client instantiation successful")
        
        # Test analyzer
        print("7. Testing analyzer...")
        analyzer = openreplay_mcp_server.SessionAnalyzer()
        print("   ✅ Analyzer instantiation successful")
        
        # Test MCP server
        print("8. Testing MCP server...")
        mcp = openreplay_mcp_server.mcp
        print(f"   MCP server type: {type(mcp)}")
        print("   ✅ MCP server accessible")
        
    except Exception as e:
        print(f"   ❌ Module import failed: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()

print("\nCompilation test complete!")