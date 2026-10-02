---
title: BiteSize: The Open-Source Anti-Overwhelm Agent I Built for My Best Friend Aarav
published: true
tags: devchallenge, weekendchallenge, hf26challenge
---

*This is a submission for the [Hacktoberfest Weekend Challenge: Build for a Friend](https://dev.to/challenges/hacktoberfest-weekend-2026-10-01)*

---

## What I Built

### Who I Built It For
I built **BiteSize** for my closest friend and roommate, **Aarav**. 

Aarav is an exceptionally talented computer science senior. When he enters hyperfocus, he can construct distributed database prototypes and optimize complex algorithms without flinching. But like many brilliant neurodivergent minds with **ADHD**, Sunday evenings are a recurring nightmare.

When a messy week catches up to him—unwashed dishes, clothes strewn across the floor, broken lab code, unread messages from his parents, and impending assignment deadlines—his brain hits a physiological roadblock known as **ADHD Executive Dysfunction Freeze**.

To a neurotypical person, a to-do list is a series of simple tasks. To Aarav's ADHD brain, the list looks like an insurmountable, 400-pound boulder. The sheer cognitive friction causes panic, shame, and paralysis. He ends up stuck in bed for hours, staring at his phone, trapped in a spiral of guilt.

Every commercial to-do app he tried (Notion, Todoist, Apple Reminders) made it worse. They presented 30 red overdue badges, rigid hierarchies, and loud notifications that screamed: *"Look how far behind you are!"*

As Aarav put it to me:
> *"I don't need another app telling me I'm failing. I just need someone to tell me where to put my first foot."*

### What BiteSize Does
**BiteSize is an autonomous, open-source AI agent built to de-escalate cognitive overload.** 

Instead of demanding structured inputs, BiteSize lets Aarav dump his raw, unfiltered, frantic stream-of-consciousness:
> *"My room is a disaster clothes on floor desk covered in cups I have to finish my ML lab report due tonight but my code is broken and I haven't eaten lunch and need to reply to mom's message and wash dishes before roommate comes home..."*

The BiteSize agent ingests this panic dump and executes an autonomous de-escalation workflow:
1. **Identifies the Core Friction Blocker**: Detects what the brain is magnifying and isolates physiological needs (e.g. low blood sugar) before intellectual chores.
2. **Decomposes the Mountain into "Atomic 2-Minute Steps"**: Strictly enforces that every sub-task takes ≤ 120 seconds and requires minimal physical friction (e.g. *"Pick up 3 shirts and drop them into the hamper. Just 3. Don't fold anything."*).
3. **Anti-Paralysis Focus Mode (The Blindfold)**: Unlike standard to-do lists, BiteSize **hides every other task**. The user only sees ONE single 2-minute pebble at a time.
4. **Virtual Body Doubler & Dopamine Engine**: Accompanies the user with calm, non-judgmental presence, an embedded circular 2-minute visual countdown, synthesized calming Brown Noise, and celebratory micro-rewards.

---

## Demo

- **Interactive Terminal UI (TUI)**: Fast, zero-distraction terminal mode powered by `rich`.
- **Responsive Web Dashboard**: Clean dark interface featuring real-time Web Audio Brown Noise synthesis, circular countdown timers, and dopamine confetti.

![BiteSize Architecture & Workflow](https://raw.githubusercontent.com/yashraghubanshi/bitesize-agent/main/docs/architecture.png)

### Live Workflow Walkthrough:
1. Run `python3 cli.py --sample` to see Aarav's messy backlog deconstructed in real-time.
2. Or start the dashboard with `python3 cli.py --web` to experience the single-step focus mode and ambient noise.

---

## Code


The complete source code is open source and hosted on GitHub:

{% github https://github.com/yashraghubanshi/bitesize-agent %}

### Core Repository Structure:
- `bitesize/agent.py`: Autonomous agent harness orchestrating perception, reasoning, and tool calls.
- `bitesize/llm_client.py`: Open-weight model adapter (Ollama with Llama 3.2 / Mistral, plus an embedded offline fallback engine).
- `bitesize/tools.py`: Tool definitions (`TaskDecomposer`, `CognitiveFrictionAnalyzer`, `BodyDoubler`, `DopamineTracker`).
- `bitesize/tui.py`: Rich terminal user interface for keyboard-driven focus.
- `api.py`: FastAPI server bridging the Python agent with modern client interfaces.
- `web/`: Vanilla HTML/CSS/JS frontend with Web Audio API brown noise generator.
- `devrelay_export.py`: Normalized agent transcript generator for DevRelay.

---

## How I Built It

### The Open-Source AI Stack
BiteSize is engineered from the ground up around open-source AI:

1. **Open-Weight Foundation Models**:
   - Primary: **Meta Llama 3.2 (3B Instruct)** and **Mistral (7B)** served via **Ollama**.
   - These models excel at structured JSON formatting, zero-shot task decomposition, and empathetic role-playing while fitting comfortably in 4GB–8GB of RAM on everyday consumer laptops.

2. **Autonomous Agent Harness**:
   - Built in **Python 3** using a structured loop:
     $$\text{Perception (Panic Dump)} \rightarrow \text{Cognitive Analysis} \rightarrow \text{Tool Decomposition} \rightarrow \text{Focus Grounding}$$
   - Strict Pydantic schemas validate that the AI output adheres to neurodivergent-safe constraints (e.g. `estimated_seconds <= 120`).

3. **Multi-Domain De-escalation Tools**:
   - `TaskDecomposerTool`: Slices high-friction tasks into concrete physical movements.
   - `BodyDoublingCompanionTool`: Uses open-weight prompting to provide psychological safety without patronizing toxic positivity.
   - `DopamineTrackerTool`: Calculates streak momentum and reward milestones.
   - `SensoryReliefTool`: Web Audio API noise synthesis generating calibrated Brownian noise (1/f² spectral density) to suppress sensory distractions.

4. **Resilient Local Fallback Engine**:
   - If a friend doesn't have an Ollama daemon installed or is running on a low-spec battery-saver machine, BiteSize includes an embedded deterministic semantic engine that operates with zero delay and 0 MB RAM footprint.

---

## Why Does Open Innovation Matter?

Open innovation wasn't just a design preference for BiteSize; **it was an ethical and practical necessity.**

### 1. Radical Privacy for Vulnerable Mental States
A brain-dump is not standard work text. When someone is in an executive dysfunction spiral, their brain dump contains deeply personal, vulnerable confessions: unfiled taxes, medical appointments they've avoided for months, academic failure fears, hygiene struggles, and family friction.

Sending that raw data to closed corporate APIs (OpenAI, Anthropic) means transmitting a person's deepest vulnerabilities to remote third-party servers where it could be logged, reviewed, or used for model retraining. **With open weights running locally via Ollama, Aarav's thoughts never leave his device. Period.**

### 2. Airplane-Mode Reliability (Zero Distractions)
When someone with ADHD is overwhelmed, their biggest enemy is the internet itself. Opening a browser to an API-dependent cloud tool invites Slack pings, YouTube notifications, and instant rabbit holes. BiteSize runs 100% offline. Aarav can disconnect Wi-Fi, put his laptop in Airplane Mode, and get unblocked without digital noise.

### 3. Zero Cost & Eternal Access
Commercial mental health and ADHD tools are infamous for putting basic productivity behind $15–$30/month subscription paywalls. Students and people battling burnout cannot afford recurring subscription guilt. Because BiteSize is built on open-weight models, it is free forever, with zero token fees.

### 4. Custom Tuning for Neurodivergence
Closed models often refuse to be concise or insist on preachy, corporate boilerplate ("As an AI assistant, I recommend you make a to-do list..."). With open weights, we can tune system prompts, control temperature, adjust logits, or fine-tune small models specifically on ADHD cognitive workflows.

---

## Handover & Aarav's Reaction (Bonus Points!)

On Sunday afternoon, I sat next to Aarav, pulled up BiteSize on his laptop, and told him to pour his messy panic into the prompt. 

He dumped 15 frantic sentences about his messy room, his broken ML lab, and his missed messages. BiteSize analyzed the friction, synthesized a calming background hum, and presented only **Step 1**:

> **"Pick up 3 pieces of clothing from the floor and drop them into the hamper. Just 3. Don't fold anything."**  
> *Timer: 90 seconds.*

Here is what Aarav said verbatim:

> *"Bro, usually looking at my to-do list makes me want to close my laptop and go back to sleep. Seeing just 'Put 3 shirts in the basket' with a 2-minute countdown actually made me get off the bed. This is the first time an app didn't make me feel guilty."*

Within 40 minutes, he had cleared his room, drunk water, eaten lunch, and written the first test case for his lab report. The paralysis was broken.

---

## My Agent Session

This project was built and recorded using **DevRelay** and the Antigravity agentic harness. You can inspect the full tool calls, prompt logs, and decision trees preserved in our normalized session:

{% agent_session 364 %}

*(Direct Session Link: [dev.to/agent_sessions/bitesize-de-escalating-adhd-task-paralysis-with-open-source-ai-zqzifx](https://dev.to/agent_sessions/bitesize-de-escalating-adhd-task-paralysis-with-open-source-ai-zqzifx))*

---

## Prize Categories

- **Hacktoberfest Weekend Challenge: Build for a Friend** (Primary)
- **Open-Source AI & Local Inference**

---

*Built with 💚 for Aarav, and for anyone who has ever felt paralyzed by their own to-do list.*
