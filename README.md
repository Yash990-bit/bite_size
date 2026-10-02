# 🌱 BiteSize — Open-Source ADHD Task De-Overwhelmer Agent

> **Built for Hacktoberfest Weekend Challenge: *Build for a Friend***  
> Dedicated with love to **Aarav** 💚

BiteSize is an autonomous, open-source AI agent built to conquer **ADHD paralysis and executive dysfunction**. When an overwhelmed brain perceives a mountain of tasks, BiteSize ingests unstructured, emotional panic dumps, analyzes cognitive friction, and shreds the mountain into microscopic, unambiguous **2-minute atomic micro-steps**—presenting them one by one in an anti-paralysis focus mode with zero guilt.

---

## 💡 The Story: Why I Built This for Aarav

Aarav is my closest friend and roommate. He is a brilliant computer science student who can write high-performance distributed systems in a flow state. But when faced with messy Sunday backlogs—chores, unread messages, broken lab assignments, and chores—his brain hits **executive dysfunction freeze**.

To an ADHD brain, a to-do list doesn't look like steps; it feels like an insurmountable 400-pound boulder. Commercial apps (Todoist, Notion) made it worse by splashing red overdue badges and guilt.

> *"I don't need another list telling me how far behind I am. I just need someone to tell me where to put my first foot."* — Aarav

BiteSize was built to be that compassionate partner. It never lectures, never shames, and hides everything except the single 2-minute step in front of you.

---

## 🧠 Open-Source AI at its Core

BiteSize is built around **open innovation**:
- **Local Open-Weight Models**: Direct support for `llama3.2:3b`, `mistral:7b`, `qwen2.5:3b`, and `phi3:mini` via **Ollama**.
- **Embedded Local Neural Fallback**: Runs 100% offline with zero external dependencies when GPU/Ollama is unavailable.
- **100% Client-Side Privacy**: Raw, vulnerable emotional thoughts, personal struggles, and health states never leave your laptop or get fed into closed corporate training sets.
- **Zero Cost / Zero Subscriptions**: Free forever, unmetered, works on an airplane in offline mode.

---

## 🏗️ Architecture

```
                       ┌───────────────────────────────────────────────┐
                       │   User Panic Dump (CLI / Voice / Web UI)      │
                       └──────────────────────┬────────────────────────┘
                                              │
                                              ▼
                       ┌───────────────────────────────────────────────┐
                       │             BiteSize Agent Loop               │
                       │   (Sense -> Reason -> Plan -> Tool -> Ground) │
                       └───────┬───────────────────────────────┬───────┘
                               │                               │
            ┌──────────────────┴───────────────┐               │
            ▼                                  ▼               ▼
 ┌──────────────────────┐         ┌─────────────────────┐  ┌─────────────────────┐
 │  Local Ollama Engine │   OR    │   Local Heuristics  │  │   Agent Tool Suite  │
 │ (Llama 3.2, Mistral) │         │    Neural Engine    │  │ - TaskDecomposer    │
 └──────────────────────┘         └─────────────────────┘  │ - BodyDoubler       │
                                                           │ - DopamineTracker   │
                                                           │ - PlanExporter      │
                                                           └──────────┬──────────┘
                                                                      │
                                              ┌───────────────────────┴───────────────┐
                                              ▼                                       ▼
                                   ┌──────────────────────┐               ┌──────────────────────┐
                                   │ Rich Interactive TUI │               │ Responsive Web App   │
                                   │ (Keyboard Focus Mode)│               │ (Binaural Brown Noise│
                                   │                      │               │  & Circular Timer)   │
                                   └──────────────────────┘               └──────────────────────┘
```

---

## 🚀 Quickstart

### 1. Prerequisites
Python 3.10+ installed.

### 2. Clone and Setup
```bash
git clone https://github.com/Yash990-bit/bite_size.git
cd bite_size
python3 -m pip install rich pydantic fastapi uvicorn requests httpx
```

### 3. Launch Interactive Terminal UI (TUI)
```bash
# Run with interactive prompt
python3 cli.py

# Or test with Aarav's real Sunday panic backlog
python3 cli.py --sample
```

### 4. Launch Modern Web Dashboard
```bash
python3 cli.py --web
# Opens automatically at http://localhost:8000
```

---

## 🎯 Key Features

1. **Anti-Paralysis Focus Mode**: Hides the other 20 steps. The user's screen only displays ONE atomic 2-minute step at a time.
2. **2-Minute Micro-Timer**: Visual circular timer that proves to the brain how short the task actually is.
3. **Web Audio Brown Noise**: Built-in real-time synthesized soothing brown noise for ADHD sensory calm (no external MP3 downloads).
4. **Dopamine Streak Engine**: Earn momentum points and celebratory feedback on every tiny win.
5. **DevRelay Integration**: Full agent session logging compatible with DEV.to and MLH hackathon submission standards.

---

## 📊 DevRelay Session Export

To export the agent trajectory and embed it in your DEV article:
```bash
python3 devrelay_export.py
```
This generates `devrelay_session.json` which can be synced directly via:
```bash
devrelay login
devrelay sessions submit --title "BiteSize: De-escalating ADHD Task Paralysis" --file devrelay_session.json
```

---

## 🤝 Handover & Aarav's Reaction

> *"Bro, usually looking at my to-do list makes me want to close my laptop and sleep. Seeing just 'Put 3 shirts in the basket' with a 2-minute countdown actually made me get off the bed. This is the first time an app didn't make me feel guilty."*  
> — **Aarav** (Roommate & Best Friend)

---

## 📄 License
MIT License. Open source forever.
