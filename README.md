# J.A.R.V.I.S – Voice‑Driven AI Desktop Assistant

Elegant, extensible desktop assistant built with Python. Speak naturally to open apps and websites, run web searches, chat with an AI model, generate content, and interact via a sleek PyQt5 UI.

---

## ✨ Features

- **Voice control (headless Chrome)** – Recognizes speech via a lightweight browser capture (`Backend/SPEECH_TO_TEXT/SpeechToText.py`).
- **Smart command router** – Routes queries to tasks like open/close/play/system/content/search (`Backend/MODEL/Model.py` → `Backend/AUTOMATION/Automation.py`).
- **Direct app/website launch** – Opens Instagram, Facebook, YouTube, etc. directly (no search results).
- **AI Chatbot (Groq)** – Chat with an AI assistant using `Groq` API (`Backend/CHATBOT/Chatbot.py`).
- **Real‑time search** – Queries the web and returns summarized results.
- **Text‑to‑Speech** – Speaks responses aloud (`Backend/TEXT_TO_SPEECH/TextToSpeech.py`).
- **Modern UI** – PyQt5 interface with animated visuals (`Frontend/GUI.py`).

---

## 🧭 Project Structure

```
.
├─ main.py                         # Entry point (starts UI + background thread)
├─ Backend/
│  ├─ AUTOMATION/Automation.py     # Open/close apps, web actions, content writer
│  ├─ CHATBOT/Chatbot.py           # ChatBot(Query) using Groq
│  ├─ IMAGE_GENERATION/            # (Optional) Image generation support
│  ├─ MODEL/Model.py               # Decision/intent router (FirstLayerDMM)
│  ├─ REAL_TIME_SEARCH_ENGINE/     # Real-time web search
│  ├─ SPEECH_TO_TEXT/SpeechToText.py  # Speech recognition (Selenium + Chrome)
│  └─ TEXT_TO_SPEECH/TextToSpeech.py  # TTS engine
├─ Frontend/
│  ├─ GUI.py                       # PyQt5 UI
│  ├─ Graphics/                    # UI assets (png/gif)
│  └─ Files/                       # Runtime files (status, responses)
├─ Data/
│  ├─ ChatLog.json                 # Conversation log
│  └─ Voice.html                   # Generated speech page (runtime)
├─ Requirements.txt
├─ .env                            # Local secrets (ignored by git)
├─ .env.example                    # Example env (placeholders)
└─ .gitignore
```

---

## ⚙️ Requirements

- Python 3.11+
- Google Chrome (for headless capture) and matching chromedriver (auto-managed)

Install dependencies:

```bash
python -m venv .venv
. .venv/Scripts/activate  # on Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r Requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` in the project root (this file is ignored by git). Example:

```env
CohereAPIKey=YOUR_COHERE_KEY
Username=YOUR_NAME
Assistantname=J.A.R.V.I.S
GroqAPIKey=YOUR_GROQ_KEY
InputLanguage=en
AssistantVoice=en-CA-LiamNeural
HuggingFaceAPIKey=YOUR_HF_KEY
```

A safe template is provided in `.env.example`. Duplicate and fill:

```bash
cp .env.example .env
```

> Never commit real API keys. The repo’s `.gitignore` prevents `.env` from being tracked.

---

## ▶️ Run

```bash
# from project root
python main.py
```

- UI will launch with an initial screen and a chat view.
- A background thread listens for microphone status and triggers the main execution loop.

---

## 🗣️ Voice & Commands

Speak naturally. The model routes your request to functions. Examples:

- "open instagram" → opens https://www.instagram.com/
- "open facebook page" → opens https://www.facebook.com/
- "play despacito" → plays on YouTube
- "google search quantum computing"
- "youtube search python decorators"
- "content Write a professional email about leave request"
- "system volume up" / "system mute"
- "close chrome"

All command routing happens in `Backend/AUTOMATION/Automation.py` and the decision layer in `Backend/MODEL/Model.py`.

---

## 🧠 Notes on Implementation

- `Automation.OpenApp()` first tries to open a native app via `AppOpener`. If not found, it smartly opens mapped websites (Instagram, Facebook, YouTube, etc.). As a fallback it parses Google results.
- Speech recognition uses a generated `Data/Voice.html` with Web Speech API, controlled via Selenium in headless Chrome.
- The chatbot uses Groq’s Chat Completions API (streaming), and appends to `Data/ChatLog.json`.
- Logs/noise from Chrome/TensorFlow are reduced with safe flags and env settings.

---

## 🧩 Customization

- Add more website shortcuts in `Automation.OpenApp()` under `website_keywords`.
- Tweak UI assets in `Frontend/Graphics/`.
- Modify voice/language through `.env` (`InputLanguage`, `AssistantVoice`).

---

## 🤝 Contributing

1. Fork this repo.
2. Create a feature branch: `git checkout -b feature/awesome`
3. Commit changes: `git commit -m "feat: add awesome thing"`
4. Push: `git push origin feature/awesome`
5. Open a Pull Request.

---

## 🛡️ Security

- Do not commit `.env` or API keys. If exposed, rotate immediately and purge history (BFG/git-filter-repo).

---

## 📄 License

This project is provided as‑is. You may adapt it for personal/educational use. Add a LICENSE file if you plan broader distribution.
