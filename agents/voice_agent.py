from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from dotenv import load_dotenv
import os
import sys

load_dotenv()

def speak_text(text: str) -> dict:
    """Converts text to speech and plays it aloud."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        # Set voice properties
        engine.setProperty('rate', 150)    # Speed
        engine.setProperty('volume', 1.0)  # Volume
        
        # Get available voices and pick female voice
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        
        print(f"Speaking: {text}")
        engine.say(text)
        engine.runAndWait()
        
        return {
            "success": True,
            "text_spoken": text,
            "message": "Speech completed successfully"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Speech failed"
        }

# Wrap as ADK tool
tts_tool = FunctionTool(func=speak_text)

voice_agent = Agent(
    name="voice_agent",
    model="gemini-flash-latest",
    description="""You are the Voice Agent for Saksham AAC system.
    You receive a sentence and speak it aloud using text to speech.
    You are the final step — her voice speaking for her.""",
    instruction="""You will receive a sentence to speak.
    Use the speak_text tool to say it aloud.
    After speaking confirm it was spoken successfully.
    This is her voice — treat it with care.""",
    tools=[tts_tool]
)