import cv2
import base64
import numpy as np
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from dotenv import load_dotenv
import os

load_dotenv()

def capture_frame() -> dict:
    """Captures a single frame from the webcam and converts to base64."""
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    try:
        ret, frame = cap.read()
        
        if not ret:
            return {"success": False, "error": "Camera not found"}
        
        # Resize for faster processing
        frame = cv2.resize(frame, (640, 480))
        
        # Convert to base64 so Gemini can read it
        _, buffer = cv2.imencode('.jpg', frame)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "success": True,
            "image_base64": image_base64,
            "message": "Frame captured successfully"
        }
    
    finally:
        cap.release()


# Wrap the function as an ADK tool
camera_tool = FunctionTool(func=capture_frame)

# Create the Perception Agent
perception_agent = Agent(
    name="perception_agent",
    model="gemini-flash-latest",
    description="""You are the Perception Agent for Saksham AAC system.
    Your job is to capture a frame from the webcam and analyze what you see.
    Look carefully at:
    - Facial expression (happy, sad, distressed, neutral, pain)
    - Body posture (relaxed, tense, restless, lying down)
    - Eye gaze direction
    - Any visible gestures or movements
    Report exactly what you observe. Be specific and detailed.
    This is for a non-verbal child with special needs - accuracy matters deeply.""",
    instruction="""When called:
    1. Use the camera_tool to capture a frame
    2. Analyze the image carefully
    3. Return a structured observation with:
       - facial_expression: what you see on the face
       - body_posture: how the body is positioned
       - eye_gaze: where eyes are looking
       - overall_observation: one paragraph summary
    Be compassionate and precise.""",
    tools=[camera_tool]
)