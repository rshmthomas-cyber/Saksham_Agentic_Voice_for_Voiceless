import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from agents.perception_agent import perception_agent

async def test():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="saksham",
        user_id="tintu",
        session_id="test1"
    )
    runner = Runner(
        agent=perception_agent,
        app_name="saksham",
        session_service=session_service
    )
    print("Testing Perception Agent...")
    print("-" * 40)
    from google.genai.types import Content, Part
    message = Content(
        role="user",
        parts=[Part(text="Capture and analyze what you see")]
    )
    async for event in runner.run_async(
        user_id="tintu",
        session_id="test1",
        new_message=message
    ):
        if event.is_final_response():
            print("Agent Response:")
            if event.content and event.content.parts:
                print(event.content.parts[0].text)
            else:
                print("Raw event:", event)
asyncio.run(test())