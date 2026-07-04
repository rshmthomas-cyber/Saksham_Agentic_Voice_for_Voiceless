# Saksham AAC 🎙️
## Agentic Voice for the Voiceless

> *"Every child deserves a voice. Saksham gives one."*

## The Story Behind This Project

Saksham was built for my daughter — a non-verbal child with special needs who 
cannot express her feelings, needs, or pain in words. As her mother and an 
AI/ML engineer, I asked myself: what if AI could see what she feels and speak 
for her?

This is that answer.

---

## What is Saksham?

Saksham (Sanskrit for "capable") is a real-time, 4-agent agentic AI system 
that:
- 👁️ **Sees** a child through a webcam
- 🧠 **Understands** their emotional state and needs
- 💬 **Forms** natural sentences in their unique voice
- 🔊 **Speaks** those words aloud for them

Built as a capstone for the **Google × Kaggle 5-Day AI Agents Intensive**, 
submitted under the **Agents for Good** track.

---

## Architecture
```
Camera Input
↓
Agent 1 — Perception (OpenCV + Gemini Vision)
↓
Agent 2 — Emotion Detection (Gemini Flash + Confidence Score)
↓ ← Human-in-the-Loop if confidence < 0.70
Agent 3 — Communication (LLM forms her sentence)
↓
Agent 4 — Voice Output (pyttsx3 TTS speaks for her)
```
---

## Course Concepts Demonstrated

| Concept | Implementation |
|---|---|
| ✅ Multi-agent systems (Google ADK) | 4 specialized ADK agents |
| ✅ Agent tools & skills | FunctionTool for camera + TTS |
| ✅ Human-in-the-Loop | Caregiver alert when confidence < 0.70 |
| ✅ Security | API keys in .env, no data persistence |
| ✅ Evals | 5-scenario test suite, 100% accuracy |
| ✅ Retry mechanism | Auto-retry on 503 errors |

---

## Evaluation Results
```
RESULTS:          5/5 passed
ACCURACY:         100.0%
AVG CONFIDENCE:   0.93
HITL TRIGGERED:   2 times
```
---

## Tech Stack

- **Google ADK** — Multi-agent orchestration
- **Gemini Flash** — Vision + emotion understanding
- **OpenCV** — Webcam capture
- **pyttsx3** — Offline text-to-speech
- **Python 3.10** — Core language
- **python-dotenv** — Secure API key management

---

## How to Run

### Prerequisites
- Python 3.10
- Google AI Studio API key
- Webcam

### Setup

```bash
# Clone the repo
git clone https://github.com/rshmthomas-cyber/Saksham_Agentic_Voice_for_Voiceless.git
cd Saksham_Agentic_Voice_for_Voiceless

# Create virtual environment
py -3.10 -m venv capstone-env
capstone-env\Scripts\activate

# Install dependencies
pip install google-adk google-generativeai opencv-python numpy python-dotenv pyttsx3

# Create .env file
echo GOOGLE_API_KEY=your_key_here > .env
echo GOOGLE_GENAI_USE_VERTEXAI=FALSE >> .env

# Run Saksham
python main.py

# Run evaluations
python evals.py
```

---

## Security

- ✅ API keys stored in `.env` — never committed to GitHub
- ✅ `.env` listed in `.gitignore`
- ✅ No user data stored — all processing in session memory
- ✅ No images or audio transmitted externally beyond Gemini API call
- ✅ Logging set to ERROR level only — no sensitive data in logs

---

## Future Roadmap

- 🔜 Fine-tuned LLaVA model on child's personal data
- 🔜 Custom ElevenLabs voice clone built from her sounds
- 🔜 Deploy on NVIDIA Jetson Orin Nano (offline, private)
- 🔜 English and Malayalam language support
- 🔜 Mobile app for caregivers

---

## Author

**Reshma Thomas** — AI/ML Engineer & Editor  
[LinkedIn](https://linkedin.com/in/reshma-thomas-nobel) | 
[GitHub](https://github.com/rshmthomas-cyber)

*Built with love, for my daughter.* 💙
