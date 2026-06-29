import asyncio
import json
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from agents.perception_agent import perception_agent
from agents.emotion_agent import emotion_agent
from agents.communication_agent import communication_agent
from agents.voice_agent import voice_agent
from dotenv import load_dotenv
import os

load_dotenv()

# One session service for all agents
session_service = InMemorySessionService()

async def run_agent(agent, session_id, message_text):
    """Helper to run any agent and get response."""
    await session_service.create_session(
        app_name="saksham",
        user_id="caregiver",
        session_id=session_id
    )
    runner = Runner(
        agent=agent,
        app_name="saksham",
        session_service=session_service
    )
    message = Content(
        role="user",
        parts=[Part(text=message_text)]
    )
    async for event in runner.run_async(
        user_id="caregiver",
        session_id=session_id,
        new_message=message
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                return event.content.parts[0].text
    return None

async def saksham_pipeline():
    """The full 4-agent Saksham pipeline."""
    print("=" * 50)
    print("SAKSHAM AAC - Agentic Voice for the Voiceless")
    print("=" * 50)
    print()
    
    # AGENT 1 - Perception
    print("Agent 1 - Perceiving...")
    observation = await run_agent(
        perception_agent,
        "session_perception",
        "Capture and analyze what you see"
    )
    print(f"Observation: {observation}")
    print()
    
    if not observation:
        print("Perception failed. Check webcam.")
        return
    
    # AGENT 2 - Emotion Detection
    print("Agent 2 - Detecting emotion...")
    emotion_result = await run_agent(
        emotion_agent,
        "session_emotion",
        f"Analyze this observation: {observation}"
    )
    print(f"Emotion Result: {emotion_result}")
    print()
    
    # HUMAN IN THE LOOP - check if caregiver needed
    try:
        emotion_data = json.loads(emotion_result)
        if emotion_data.get("needs_caregiver"):
            print("⚠️  LOW CONFIDENCE — Caregiver input needed!")
            print(f"Best guess: {emotion_data.get('emotion')}")
            caregiver_input = input("What does she need? (press Enter to use best guess): ")
            if caregiver_input.strip():
                emotion_result = json.dumps({
                    "emotion": caregiver_input,
                    "confidence": 1.0,
                    "needs_caregiver": False,
                    "urgency": "normal"
                })
    except:
        pass
    
    # AGENT 3 - Communication
    print("Agent 3 - Finding her words...")
    sentence = await run_agent(
        communication_agent,
        "session_communication",
        f"Create her sentence from: {emotion_result}"
    )
    print(f"Her words: {sentence}")
    print()
    
    # AGENT 4 - Voice
    print("Agent 4 - Speaking for her...")
    await run_agent(
        voice_agent,
        "session_voice",
        f"Please speak this: {sentence}"
    )
    
    print()
    print("=" * 50)
    print("Pipeline complete!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(saksham_pipeline())