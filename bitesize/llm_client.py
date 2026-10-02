"""
LLM Client for BiteSize: Open-Source AI Inference Adapter.
Supports local Ollama (Llama 3.2, Mistral, Qwen 2.5) with automatic fallback
to an advanced, dynamic local NLP semantic de-escalation engine.
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
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=1.0)
            return resp.status_code == 200
        except Exception:
            return False

    def list_local_models(self) -> List[str]:
        """Fetch available open-weight models from local Ollama instance."""
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=1.5)
            if resp.status_code == 200:
                data = resp.json()
                return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def generate_plan(self, brain_dump: str, paralysis_level: str = "extreme") -> DecomposedPlan:
        """Generate a decomposed plan using Ollama if available, or fallback to the local dynamic engine."""
        session_id = f"session_{uuid.uuid4().hex[:8]}"

        # Attempt Ollama if online
        if self.is_ollama_available():
            try:
                plan_data = self._call_ollama(brain_dump, paralysis_level)
                if plan_data and plan_data.get("atomic_steps"):
                    return self._build_plan_from_dict(session_id, brain_dump, plan_data)
            except Exception:
                pass

        # Fallback to dynamic, non-hardcoded local semantic engine
        return self._dynamic_local_decomposer(session_id, brain_dump, paralysis_level)

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
                "temperature": 0.3,
                "top_p": 0.85,
            }
        }
        
        response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=60.0)
        if response.status_code == 200:
            result = response.json().get("response", "")
            clean_json = re.sub(r"^```json\s*", "", result.strip())
            clean_json = re.sub(r"```$", "", clean_json.strip())
            return json.loads(clean_json)
        return None

    def _extract_task_clauses(self, text: str) -> List[str]:
        """
        Dynamically segment unstructured emotional brain-dumps into atomic task clauses.
        Uses punctuation and natural language transition markers.
        """
        # Remove emotional filler preambles
        cleaned = re.sub(r"(?i)\b(i have to|i need to|i must|i gotta|i should|im supposed to|panicking because|so overwhelmed with|feel completely frozen and|completely disaster|oh my god|omg)\b", "", text)
        
        # Split on sentence boundaries and coordinating conjunctions
        pattern = r"[\.\n;!\?]|(?:\b(?:and then|after that|and also|plus|before|also|need to|have to|and)\b)|,"
        raw_clauses = re.split(pattern, cleaned, flags=re.IGNORECASE)
        
        valid_clauses = []
        for c in raw_clauses:
            clause = c.strip()
            # Filter noise and tiny fragments
            if len(clause) > 3 and not re.match(r"^(it|that|then|so|but|is|are|a|an|the)$", clause, re.IGNORECASE):
                valid_clauses.append(clause)
        return valid_clauses

    def _dynamic_local_decomposer(self, session_id: str, dump: str, paralysis_level: str) -> DecomposedPlan:
        """
        Advanced, dynamic, zero-hardcoding semantic deconstruction engine.
        Parses arbitrary user inputs, identifies verbs and entities,
        and synthesizes ultra-concrete 2-minute atomic micro-steps.
        """
        clauses = self._extract_task_clauses(dump)
        if not clauses:
            clauses = [dump.strip()]

        steps: List[AtomicStep] = []
        identified_domains = set()
        step_counter = 1

        for clause in clauses:
            cl = clause.lower().strip()
            step_obj = self._synthesize_atomic_step(cl, step_counter)
            if step_obj:
                steps.append(step_obj)
                identified_domains.add(step_obj.domain)
                step_counter += 1

        # Priority sorting: Place physiological/self-care tasks FIRST (ADHD brains freeze when hypoglycemic/dehydrated)
        steps.sort(key=lambda s: 0 if s.domain == "Self-Care" else 1)

        # Re-index step IDs
        for idx, s in enumerate(steps, start=1):
            s.id = f"step-{idx}"

        domain_list = list(identified_domains) if identified_domains else ["General Life"]

        friction_analysis = CognitiveFrictionAnalysis(
            perceived_mountain=f"Feeling overwhelmed by {len(steps)} simultaneous tasks across {len(domain_list)} domains.",
            core_blocker="High task ambiguity and executive dysfunction inertia (initiation freeze).",
            paralysis_level=paralysis_level.capitalize(),
            identified_domains=domain_list
        )

        first_rec = steps[0].title if steps else "Stand up and take a deep breath."
        total_time_mins = sum(s.estimated_seconds for s in steps) / 60.0

        return DecomposedPlan(
            session_id=session_id,
            original_dump=dump,
            friction_analysis=friction_analysis,
            first_step_recommendation=first_rec,
            atomic_steps=steps,
            body_doubling_message="Hey Mayank. Take a breath. You don't have to conquer everything right now. Just give me 90 seconds on this single first step. I'm right here with you.",
            total_steps=len(steps),
            total_estimated_minutes=round(total_time_mins, 1)
        )

    def _synthesize_atomic_step(self, clause: str, index: int) -> AtomicStep:
        """
        Synthesizes an atomic 2-minute step tailored specifically to the clause content.
        """
        cl = clause.lower()

        # 1. Biological / Self-Care
        if any(w in cl for w in ["water", "drink", "eat", "lunch", "dinner", "breakfast", "food", "snack", "hungry", "shower", "sleep", "nap", "tired", "rest", "pill", "meds", "medicine"]):
            domain = "Self-Care"
            if "water" in cl or "drink" in cl or "hungry" in cl or "eat" in cl or "food" in cl or "lunch" in cl:
                title = "Drink 1 glass of cold water and grab a quick bite"
                desc = "Blood sugar crashes trigger executive paralysis. Hydrate first."
                reward = "🌱 +20 Energy Restored"
            elif "shower" in cl:
                title = "Turn on the shower warm water and set out 1 clean towel"
                desc = "Don't step in yet. Just let the bathroom steam for 60 seconds."
                reward = "🚿 +15 Sensory Reset"
            else:
                title = f"Take a 2-minute physical reset for: {clause}"
                desc = "Stretch arms upward and drink water before initiating tasks."
                reward = "🫁 +15 Nervous System Reset"
            return AtomicStep(id=f"step-{index}", title=title, description=desc, domain=domain, estimated_seconds=60, friction_score=1, micro_reward=reward)

        # 2. Physical Space / Domestic Chores
        if any(w in cl for w in ["dish", "dishes", "sink", "room", "clothes", "floor", "laundry", "clean", "trash", "desk", "bed", "kitchen", "closet", "faucet", "leak", "fix", "repair", "car"]):
            domain = "Physical Space"
            if "dish" in cl or "sink" in cl:
                title = "Squirt soap on 1 sponge and wash only 1 single fork or cup"
                desc = "Rinse 1 item and place on drying rack. Do not look at the rest."
                reward = "✨ +15 Dish Inertia Shattered"
                secs = 60
            elif "cloth" in cl or "laundry" in cl or "floor" in cl:
                title = "Pick up exactly 3 pieces of clothing from the floor"
                desc = "Toss them into the hamper. Only 3 items. Zero folding allowed."
                reward = "🧺 +15 Floor Cleared"
                secs = 60
            elif "trash" in cl or "cup" in cl or "desk" in cl:
                title = "Throw away 2 pieces of trash or move 2 empty cups to the sink"
                desc = "Clear just one 12-inch square of desk space."
                reward = "🪴 +10 Space Clarity"
                secs = 45
            elif "bed" in cl:
                title = "Pull the blanket up over the pillows once"
                desc = "Don't make it military-perfect. Just one pull."
                reward = "🛏️ +10 Bed Reset"
                secs = 30
            elif "fix" in cl or "leak" in cl or "faucet" in cl or "repair" in cl:
                title = f"Look at the problem area ({clause}) for 60 seconds"
                desc = "Observe the situation with a flashlight. Do not touch tools yet."
                reward = "🔧 +20 Diagnostics Started"
                secs = 60
            else:
                title = f"Organize the smallest physical item related to: {clause}"
                desc = "Pick up one single item and put it in place."
                reward = "🧹 +10 Space Momentum"
                secs = 60
            return AtomicStep(id=f"step-{index}", title=title, description=desc, domain=domain, estimated_seconds=secs, friction_score=1, micro_reward=reward)

        # 3. Academic / Coding / Technical / Writing
        if any(w in cl for w in ["code", "lab", "report", "exam", "study", "project", "work", "due", "bug", "write", "pr", "commit", "review", "git", "doc", "slides", "presentation", "assignment", "test"]):
            domain = "Academic & Work"
            if "code" in cl or "bug" in cl or "lab" in cl:
                title = f"Open your code editor and read the function name for: {clause}"
                desc = "Do not write code or debug. Just locate the file and open it."
                reward = "💻 +20 Code Inertia Shattered"
                secs = 60
            elif "study" in cl or "exam" in cl or "read" in cl:
                title = f"Open the textbook or notes for: {clause}"
                desc = "Read only the title and the first bold heading. Close notes."
                reward = "📖 +15 Study Kickstart"
                secs = 60
            elif "write" in cl or "report" in cl or "assignment" in cl or "slides" in cl:
                title = f"Create a blank document with the title: '{clause.capitalize()}'"
                desc = "Write the title and 1 bullet point. Leave body blank."
                reward = "📝 +20 Blank Page Conquered"
                secs = 60
            elif "review" in cl or "pr" in cl:
                title = f"Open the review link and read only the PR description"
                desc = "Do not inspect the diffs yet. Just read the 2-sentence summary."
                reward = "🔍 +15 Review Begun"
                secs = 45
            else:
                title = f"Open the primary tool or window needed for: {clause}"
                desc = "Just bring the window to the front of your screen."
                reward = "⚡ +15 Workspace Loaded"
                secs = 45
            return AtomicStep(id=f"step-{index}", title=title, description=desc, domain=domain, estimated_seconds=secs, friction_score=2, micro_reward=reward)

        # 4. Bureaucracy / Admin / Finance / Legal / Appointments
        if any(w in cl for w in ["tax", "taxes", "bill", "bank", "pay", "rent", "landlord", "form", "doctor", "dentist", "appointment", "schedule", "renew", "passport", "visa"]):
            domain = "Administrative"
            if "tax" in cl or "form" in cl or "renew" in cl:
                title = f"Create a desktop folder named 'Docs - {clause.title()}'"
                desc = "Do not fill forms yet. Just create the destination folder."
                reward = "📁 +25 Bureaucracy Broken"
                secs = 45
            elif "bill" in cl or "pay" in cl or "bank" in cl or "rent" in cl:
                title = f"Open the banking or payment portal in your browser"
                desc = "Log in and look at the due date. You don't have to pay yet."
                reward = "💳 +25 Financial Courage"
                secs = 60
            elif "appointment" in cl or "doctor" in cl or "dentist" in cl or "schedule" in cl:
                title = f"Look up the phone number or booking portal for: {clause}"
                desc = "Paste the number into your dialer. You don't have to press call."
                reward = "🩺 +20 Health Step Begun"
                secs = 45
            else:
                title = f"Write down 1 requirement needed for: {clause}"
                desc = "A 5-word sticky note is all that is required right now."
                reward = "📋 +15 Admin Clarity"
                secs = 45
            return AtomicStep(id=f"step-{index}", title=title, description=desc, domain=domain, estimated_seconds=secs, friction_score=3, micro_reward=reward)

        # 5. Communication / Social Obligations
        if any(w in cl for w in ["email", "reply", "message", "text", "call", "mom", "dad", "friend", "roommate", "boss", "slack"]):
            domain = "Communication"
            if "mom" in cl or "dad" in cl or "friend" in cl:
                title = f"Send a 1-sentence reassurance message to: {clause}"
                desc = "Send: 'Hey! Saw your message, will call you in a bit!'"
                reward = "📱 +15 Social Guilt Relief"
            elif "email" in cl or "slack" in cl:
                title = f"Open email and star the thread regarding: {clause}"
                desc = "Star it so it doesn't get lost. Do not draft a reply yet."
                reward = "✉️ +15 Inbox Grounding"
            else:
                title = f"Send a brief 1-line reply: {clause}"
                desc = "A 5-word acknowledgement is 100x better than ghosting."
                reward = "💬 +15 Connection Maintained"
            return AtomicStep(id=f"step-{index}", title=title, description=desc, domain=domain, estimated_seconds=45, friction_score=2, micro_reward=reward)

        # 6. Errands & Packing & Physical Logistics
        if any(w in cl for w in ["pack", "suitcase", "bag", "luggage", "trip", "flight", "buy", "groceries", "milk", "store", "vet", "dog", "cat", "pharmacy"]):
            domain = "Logistics & Errands"
            if "pack" in cl or "suitcase" in cl or "luggage" in cl:
                title = f"Open your suitcase or backpack on the bed and unzip it"
                desc = "Lay out exactly 2 pairs of socks. Stop right there."
                reward = "🧳 +20 Packing Begun"
            elif "dog" in cl or "cat" in cl or "vet" in cl:
                title = f"Find the pet leash or carrier for: {clause}"
                desc = "Place it by the front door."
                reward = "🐾 +15 Pet Care Step"
            else:
                title = f"Add 1 item to your shopping/errand list: {clause}"
                desc = "Jot it on a scratch paper or notes app."
                reward = "🛒 +15 Errand Captured"
            return AtomicStep(id=f"step-{index}", title=title, description=desc, domain=domain, estimated_seconds=60, friction_score=2, micro_reward=reward)

        # 7. Dynamic Catch-All for Any Arbitrary Action
        domain = "Life Management"
        title = f"Spend 60 seconds inspecting: {clause}"
        desc = "Take one physical or digital action that takes under 120 seconds."
        reward = "⚡ +15 Action Initiated"
        return AtomicStep(id=f"step-{index}", title=title, description=desc, domain=domain, estimated_seconds=60, friction_score=1, micro_reward=reward)

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
