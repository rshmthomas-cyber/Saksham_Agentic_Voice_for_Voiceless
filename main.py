import asyncio
import json
import time
import logging

# Security: suppress sensitive data from logs
logging.basicConfig(level=logging.ERROR)
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

async def run_agent(agent, session_id, message_text, retries=3):
    """Helper to run any agent with retry on 503 errors."""
    for attempt in range(retries):
        try:
            await session_service.create_session(
                app_name="saksham",
                user_id="caregiver",
                session_id=f"{session_id}_{attempt}"
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
                session_id=f"{session_id}_{attempt}",
                new_message=message
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        return event.content.parts[0].text
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                print(f"  Gemini busy, retrying in 10 seconds... (attempt {attempt+1}/{retries})")
                time.sleep(10)
            else:
                raise
    return None

async def saksham_pipeline():
    """The full 4-agent Saksham pipeline."""
    print("=" * 50)
    print("SAKSHAM AAC - Agentic Voice for the Voiceless")
    print("=" * 50)
    print()
    
    # AGENT 1 - Perception with loopback retry
    print("Agent 1 - Perceiving...")
    max_perception_attempts = 3
    observation = None
    
    for attempt in range(max_perception_attempts):
        observation = await run_agent(
            perception_agent,
            f"session_perception_{attempt}",
            "Capture and analyze what you see"
        )
        
        if observation:
            print(f"Observation: {observation}")
            break
        else:
            print(f"  Perception attempt {attempt+1} failed, retrying...")
    
    if not observation:
        print("Perception failed after 3 attempts. Check webcam.")
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
    
    # AGENT ORCHESTRATION — confidence-based dynamic routing
    try:
        emotion_data = json.loads(
            emotion_result.replace("```json", "").replace("```", "").strip()
        )
        confidence = emotion_data.get("confidence", 0)
        
        # Below 0.50 — loop back to Agent 1 for another look
        if confidence < 0.50:
            print(f"⚠️  Very low confidence ({confidence}) — looping back to Agent 1...")
            observation = await run_agent(
                perception_agent,
                "session_perception_retry",
                "Look more carefully. Capture and analyze again."
            )
            print(f"  New observation: {observation}")
            emotion_result = await run_agent(
                emotion_agent,
                "session_emotion_retry",
                f"Analyze this carefully: {observation}"
            )
            emotion_data = json.loads(
                emotion_result.replace("```json", "").replace("```", "").strip()
            )
            print(f"  Retry emotion result: {emotion_result}")

        # Below 0.70 — trigger Human-in-the-Loop
        elif emotion_data.get("needs_caregiver"):
            print(f"⚠️  LOW CONFIDENCE ({confidence}) — Caregiver input needed!")
            print(f"   Best guess: {emotion_data.get('emotion')}")
            print(f"   Urgency: {emotion_data.get('urgency')}")
            caregiver_input = input("What does she need? (press Enter to use best guess): ")
            if caregiver_input.strip():
                emotion_data = {
                    "emotion": caregiver_input,
                    "confidence": 1.0,
                    "needs_caregiver": False,
                    "urgency": "normal"
                }
                emotion_result = json.dumps(emotion_data)
                print(f"  Caregiver confirmed: {caregiver_input}")
        else:
            print(f"✅ High confidence ({confidence}) — proceeding automatically")

    except Exception as e:
        print(f"Orchestration error: {e}")
    
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