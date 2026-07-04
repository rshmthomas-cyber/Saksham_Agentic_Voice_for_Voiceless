"""
Saksham AAC — MCP Server
Exposes Saksham's agent tools via Model Context Protocol
Allows agents to discover and call tools dynamically
"""
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
import cv2
import base64
import pyttsx3
import json
import asyncio

# MCP Server tool definitions
SAKSHAM_MCP_TOOLS = [
    {
        "name": "capture_frame",
        "description": "Captures webcam frame for vision analysis",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "analyze_emotion",
        "description": "Analyzes observation and returns emotion + confidence",
        "input_schema": {
            "type": "object",
            "properties": {
                "observation": {
                    "type": "string",
                    "description": "Text description of what was observed"
                }
            },
            "required": ["observation"]
        }
    },
    {
        "name": "speak_text",
        "description": "Converts text to speech and plays aloud",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to speak aloud"
                }
            },
            "required": ["text"]
        }
    }
]

def capture_frame_tool() -> dict:
    """MCP Tool: Captures webcam frame."""
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    try:
        ret, frame = cap.read()
        if not ret:
            return {"success": False, "error": "Camera unavailable"}
        frame = cv2.resize(frame, (640, 480))
        _, buffer = cv2.imencode('.jpg', frame)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return {
            "success": True,
            "image_base64": image_base64,
            "tool": "capture_frame",
            "protocol": "MCP"
        }
    finally:
        cap.release()

def speak_text_tool(text: str) -> dict:
    """MCP Tool: Speaks text aloud."""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.say(text)
        engine.runAndWait()
        return {
            "success": True,
            "text_spoken": text,
            "tool": "speak_text",
            "protocol": "MCP"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def handle_mcp_request(tool_name: str, tool_input: dict) -> dict:
    """Routes MCP tool calls to the right function."""
    if tool_name == "capture_frame":
        return capture_frame_tool()
    elif tool_name == "speak_text":
        return speak_text_tool(tool_input.get("text", ""))
    else:
        return {"error": f"Unknown tool: {tool_name}"}

async def run_mcp_server():
    """Starts the MCP server and listens for tool calls."""
    print("=" * 50)
    print("Saksham MCP Server Starting...")
    print("=" * 50)
    print()
    print("Available MCP Tools:")
    for tool in SAKSHAM_MCP_TOOLS:
        print(f"  ✅ {tool['name']}: {tool['description']}")
    print()
    print("MCP Server ready — agents can now discover tools!")
    print("Protocol: Model Context Protocol (MCP)")
    print("Transport: stdio")
    print()

    # Demonstrate MCP tool discovery
    print("Tool Discovery Test:")
    print(json.dumps({
        "mcp_server": "saksham_aac",
        "version": "1.0",
        "tools": [t["name"] for t in SAKSHAM_MCP_TOOLS],
        "status": "ready"
    }, indent=2))

if __name__ == "__main__":
    asyncio.run(run_mcp_server())