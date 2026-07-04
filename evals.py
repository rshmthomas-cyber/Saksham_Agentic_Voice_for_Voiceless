"""
Saksham AAC - Evaluation Framework
Tests the system's accuracy and reliability
"""
import json
import asyncio
from datetime import datetime

# Test scenarios simulating different emotional states
TEST_SCENARIOS = [
    {
        "id": 1,
        "scenario": "Child appears hungry - restless, looking toward kitchen",
        "expected_emotion": "hungry",
        "expected_urgency": "normal"
    },
    {
        "id": 2,
        "scenario": "Child is crying, body tense, arms reaching out",
        "expected_emotion": "distressed",
        "expected_urgency": "high"
    },
    {
        "id": 3,
        "scenario": "Child is smiling, relaxed, making happy sounds",
        "expected_emotion": "happy",
        "expected_urgency": "low"
    },
    {
        "id": 4,
        "scenario": "Child is lying down after meal, eyes closed, calm",
        "expected_emotion": "resting",
        "expected_urgency": "low"
    },
    {
        "id": 5,
        "scenario": "Child is grimacing, holding stomach, whimpering",
        "expected_emotion": "pain",
        "expected_urgency": "high"
    }
]

async def run_eval_scenario(scenario: dict) -> dict:
    """Run a single evaluation scenario through Agent 2."""
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai.types import Content, Part
    from agents.emotion_agent import emotion_agent
    import time

    session_service = InMemorySessionService()

    for attempt in range(3):
        try:
            await session_service.create_session(
                app_name="saksham_eval",
                user_id="eval_system",
                session_id=f"eval_{scenario['id']}_{attempt}"
            )
            runner = Runner(
                agent=emotion_agent,
                app_name="saksham_eval",
                session_service=session_service
            )
            message = Content(
                role="user",
                parts=[Part(text=f"Analyze this observation: {scenario['scenario']}")]
            )
            async for event in runner.run_async(
                user_id="eval_system",
                session_id=f"eval_{scenario['id']}_{attempt}",
                new_message=message
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        raw = event.content.parts[0].text
                        # Clean JSON from markdown
                        clean = raw.replace("```json", "").replace("```", "").strip()
                        result = json.loads(clean)
                        return {
                            "scenario_id": scenario["id"],
                            "scenario": scenario["scenario"],
                            "expected_emotion": scenario["expected_emotion"],
                            "detected_emotion": result.get("emotion"),
                            "confidence": result.get("confidence"),
                            "needs_caregiver": result.get("needs_caregiver"),
                            "urgency": result.get("urgency"),
                            "passed": result.get("emotion") == scenario["expected_emotion"]
                        }
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                print(f"  Gemini busy, retrying in 10s...")
                time.sleep(10)
            else:
                return {
                    "scenario_id": scenario["id"],
                    "error": str(e),
                    "passed": False
                }
    return {"scenario_id": scenario["id"], "error": "Max retries exceeded", "passed": False}

async def run_all_evals():
    """Run all evaluation scenarios and print report."""
    print("=" * 60)
    print("SAKSHAM AAC - Evaluation Report")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print()

    results = []
    for scenario in TEST_SCENARIOS:
        print(f"Testing scenario {scenario['id']}: {scenario['scenario'][:50]}...")
        result = await run_eval_scenario(scenario)
        results.append(result)

        if "error" not in result:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"  {status} | Expected: {result['expected_emotion']} | "
                  f"Got: {result['detected_emotion']} | "
                  f"Confidence: {result['confidence']}")
        else:
            print(f"  ❌ ERROR: {result['error']}")
        print()

    # Summary
    passed = sum(1 for r in results if r.get("passed"))
    total = len(results)
    accuracy = (passed / total) * 100

    print("=" * 60)
    print(f"RESULTS: {passed}/{total} passed")
    print(f"ACCURACY: {accuracy:.1f}%")

    avg_confidence = sum(
        r.get("confidence", 0) for r in results
        if "confidence" in r
    ) / max(len([r for r in results if "confidence" in r]), 1)
    print(f"AVG CONFIDENCE: {avg_confidence:.2f}")

    hitl_triggered = sum(
        1 for r in results
        if r.get("needs_caregiver")
    )
    print(f"HUMAN-IN-LOOP TRIGGERED: {hitl_triggered} times")
    print("=" * 60)

    # Save report
    with open("eval_report.json", "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().isoformat(),
            "total": total,
            "passed": passed,
            "accuracy": accuracy,
            "avg_confidence": avg_confidence,
            "hitl_triggered": hitl_triggered,
            "results": results
        }, f, indent=2)
    print("\nReport saved to eval_report.json")

if __name__ == "__main__":
    asyncio.run(run_all_evals())