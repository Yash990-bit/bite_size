"""
LLM Client for BiteSize: Open-Source AI Inference Adapter.
Supports local Ollama (Llama 3.2, Mistral, Qwen 2.5) with automatic fallback
to an embedded local semantic de-escalation engine.
"""
import json
import re
import uuid
import requests
from typing import Dict, Any, List, Optional
from bitesize.schemas import AtomicStep, CognitiveFrictionAnalysis, DecomposedPlan


SYSTEM_PROMPT = """You are BiteSize, an empathetic, open-source AI agent designed specifically for individuals experiencing ADHD paralysis, burnout, or severe executive dysfunction.

Your friend has dumped an unstructured, chaotic, panic-laden brain-dump.
Your objective:
1. Identify the core emotional or physical blocker causing paralysis.
2. Shred the mountain of perceived work into ultra-concrete, unambiguous, atomic micro-steps (each takes ≤ 120 seconds).
3. Ensure the VERY FIRST step has near-zero cognitive resistance (e.g. 'Pick up 3 shirts', 'Open laptop lid', 'Drink a sip of water').
4. Categorize tasks by domain (Physical Space, Academic/Work, Self-Care, Admin).
5. Output ONLY valid JSON matching this exact structure:
{
  "perceived_mountain": "string",
  "core_blocker": "string",
  "paralysis_level": "Extreme",
  "identified_domains": ["Physical Space", "Academic/Work"],
  "first_step_recommendation": "string (the exact easiest step)",
  "body_doubling_message": "string (warm, non-judgmental validation)",
  "atomic_steps": [
    {
      "id": "step-1",
      "title": "Ultra concrete 2-min action",
      "description": "Specific low-friction instruction under 20 words",
      "domain": "Physical Space",
      "estimated_seconds": 120,
      "friction_score": 1,
      "micro_reward": "✨ +10 Momentum"
    }
  ]
}
Do not include any conversational preamble or markdown backticks outside the JSON. Return only the JSON object.
"""


class OpenSourceLLMClient:
    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "llama3.2:latest"):
        self.ollama_url = ollama_url.rstrip("/")
        self.model_name = model_name

    def is_ollama_available(self) -> bool:
        """Check if local Ollama daemon is reachable."""
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=1.5)
            return resp.status_code == 200
        except Exception:
            return False

    def list_local_models(self) -> List[str]:
        """Fetch available open-weight models from local Ollama instance."""
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=2.0)
            if resp.status_code == 200:
                data = resp.json()
                return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def generate_plan(self, brain_dump: str, paralysis_level: str = "extreme") -> DecomposedPlan:
        """Generate a decomposed plan using Ollama if available, or fallback to the local engine."""
        session_id = f"session_{uuid.uuid4().hex[:8]}"

        # Attempt Ollama if online
        if self.is_ollama_available():
            try:
                plan_data = self._call_ollama(brain_dump, paralysis_level)
                if plan_data:
                    return self._build_plan_from_dict(session_id, brain_dump, plan_data)
            except Exception as e:
                # Silently fallback to embedded engine
                pass

        # Fallback to local intelligent semantic engine
        return self._local_semantic_decomposer(session_id, brain_dump, paralysis_level)

    def _call_ollama(self, brain_dump: str, paralysis_level: str) -> Optional[Dict[str, Any]]:
        """Call local Ollama open-weight model with structured JSON prompting."""
        user_prompt = f"Paralysis Level: {paralysis_level}\n\nChaotic Brain Dump:\n{brain_dump}"
        
        payload = {
            "model": self.model_name,
            "system": SYSTEM_PROMPT,
            "prompt": user_prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.4,
                "top_p": 0.9,
            }
        }
        
        response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=60.0)
        if response.status_code == 200:
            result = response.json().get("response", "")
            # Clean markdown codeblocks if model included them
            clean_json = re.sub(r"^```json\s*", "", result.strip())
            clean_json = re.sub(r"```$", "", clean_json.strip())
            return json.loads(clean_json)
        return None

    def _local_semantic_decomposer(self, session_id: str, dump: str, paralysis_level: str) -> DecomposedPlan:
        """
        Deterministic, offline, low-latency semantic de-escalation engine.
        Parses common ADHD overwhelm signals (cleaning, studies, emails, health, chores)
        and converts them into atomic micro-steps.
        """
        text_lower = dump.lower()
        steps: List[AtomicStep] = []
        domains: List[str] = []

        # Analyze physical space friction
        if any(w in text_lower for w in ["room", "clothes", "mess", "floor", "laundry", "clean", "trash", "desk"]):
            domains.append("Physical Space")
            steps.append(AtomicStep(
                id=f"step-{len(steps)+1}",
                title="Pick up 3 pieces of clothing from the floor",
                description="Drop them directly into the laundry hamper. Only 3 items. Don't fold anything.",
                domain="Physical Space",
                estimated_seconds=90,
                friction_score=1,
                micro_reward="🧺 +15 Clean Space Momentum"
            ))
            steps.append(AtomicStep(
                id=f"step-{len(steps)+1}",
                title="Clear 2 empty cups or bottles from your desk",
                description="Carry just 2 cups to the kitchen sink. Don't wash them yet, just relocate them.",
                domain="Physical Space",
                estimated_seconds=60,
                friction_score=1,
                micro_reward="💧 +10 Desk Clarity"
            ))

        # Analyze academic / work friction
        if any(w in text_lower for w in ["lab", "code", "report", "exam", "study", "project", "work", "due", "bug", "write"]):
            domains.append("Academic & Work")
            steps.append(AtomicStep(
                id=f"step-{len(steps)+1}",
                title="Open the project file and read the first paragraph or title",
                description="Do not write or debug. Just open the IDE/document and look at the screen for 60 seconds.",
                domain="Academic & Work",
                estimated_seconds=60,
                friction_score=2,
                micro_reward="💻 +20 Inertia Shattered"
            ))
            steps.append(AtomicStep(
                id=f"step-{len(steps)+1}",
                title="Write 1 bullet point or run 1 test command",
                description="Write one single sentence or comment in the file. Perfection is strictly prohibited.",
                domain="Academic & Work",
                estimated_seconds=120,
                friction_score=2,
                micro_reward="⚡ +25 Focus Kickstart"
            ))

        # Analyze communication / social / admin friction
        if any(w in text_lower for w in ["email", "reply", "mom", "dad", "message", "call", "form", "bill", "tax", "pay"]):
            domains.append("Administrative & Social")
            steps.append(AtomicStep(
                id=f"step-{len(steps)+1}",
                title="Send a 1-sentence placeholder message",
                description="Send: 'Hey! Got your message, busy right now but will call you by 7 PM!'",
                domain="Administrative & Social",
                estimated_seconds=45,
                friction_score=2,
                micro_reward="📱 +15 Social Relief"
            ))

        # Analyze self-care / nutrition friction
        if any(w in text_lower for w in ["eat", "lunch", "dinner", "food", "hungry", "water", "shower", "tired", "sleep"]):
            domains.append("Self-Care")
            # Put self-care first if detected!
            self_care_step = AtomicStep(
                id=f"step-selfcare",
                title="Drink a glass of cold water and grab a quick snack",
                description="ADHD brains freeze when blood sugar drops. Drink 1 glass of water right now.",
                domain="Self-Care",
                estimated_seconds=60,
                friction_score=1,
                micro_reward="🌱 +20 Energy Restoration"
            )
            steps.insert(0, self_care_step)

        # Fallback if unclassified
        if not steps:
            domains.append("General Life")
            steps.append(AtomicStep(
                id="step-1",
                title="Stand up, stretch your arms, and take 3 deep belly breaths",
                description="Physical reset to snap the nervous system out of fight-or-flight freeze.",
                domain="Self-Care",
                estimated_seconds=45,
                friction_score=1,
                micro_reward="🫁 +10 Nervous Reset"
            ))
            steps.append(AtomicStep(
                id="step-2",
                title="Pick the single smallest physical item near you and put it in place",
                description="A pen, a wrapper, or a charger cable. Put it away to prove you have agency.",
                domain="Physical Space",
                estimated_seconds=60,
                friction_score=1,
                micro_reward="✨ +15 Agency Proved"
            ))

        # Re-index step IDs
        for idx, s in enumerate(steps, start=1):
            s.id = f"step-{idx}"

        friction_analysis = CognitiveFrictionAnalysis(
            perceived_mountain=f"The feeling that you have to fix everything across {len(domains)} domains all at once.",
            core_blocker="High task ambiguity and executive dysfunction inertia (ADHD task paralysis).",
            paralysis_level=paralysis_level.capitalize(),
            identified_domains=domains
        )

        first_rec = steps[0].title if steps else "Take one deep breath."
        total_time_mins = sum(s.estimated_seconds for s in steps) / 60.0

        return DecomposedPlan(
            session_id=session_id,
            original_dump=dump,
            friction_analysis=friction_analysis,
            first_step_recommendation=first_rec,
            atomic_steps=steps,
            body_doubling_message="Hey Aarav. Take a breath. You don't have to conquer your whole life today. Just give me 2 minutes on this single first step. I'm right here with you.",
            total_steps=len(steps),
            total_estimated_minutes=round(total_time_mins, 1)
        )

    def _build_plan_from_dict(self, session_id: str, dump: str, data: Dict[str, Any]) -> DecomposedPlan:
        """Parse dictionary from Ollama into DecomposedPlan Pydantic model."""
        raw_steps = data.get("atomic_steps", [])
        steps = [AtomicStep(**s) for s in raw_steps]
        
        friction_data = {
            "perceived_mountain": data.get("perceived_mountain", "Massive multi-task backlog"),
            "core_blocker": data.get("core_blocker", "Task paralysis"),
            "paralysis_level": data.get("paralysis_level", "Extreme"),
            "identified_domains": data.get("identified_domains", ["General"])
        }
        
        total_time_mins = sum(s.estimated_seconds for s in steps) / 60.0 if steps else 0.0

        return DecomposedPlan(
            session_id=session_id,
            original_dump=dump,
            friction_analysis=CognitiveFrictionAnalysis(**friction_data),
            first_step_recommendation=data.get("first_step_recommendation", steps[0].title if steps else "Begin"),
            atomic_steps=steps,
            body_doubling_message=data.get("body_doubling_message", "You're not alone. Let's do step 1 together."),
            total_steps=len(steps),
            total_estimated_minutes=round(total_time_mins, 1)
        )
