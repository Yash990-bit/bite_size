"""
BiteSize Autonomous Agent Harness
Coordinates cognitive de-escalation, tool calling, focus tracking, and DevRelay session history.
"""
from typing import Dict, Any, List, Optional
from bitesize.schemas import DecomposedPlan, AtomicStep, UserState
from bitesize.llm_client import OpenSourceLLMClient
from bitesize.tools import (
    TaskDecomposerTool,
    BodyDoublingCompanionTool,
    DopamineTrackerTool,
    PlanExporterTool
)
from bitesize.storage import LocalStorage


class BiteSizeAgent:
    """
    Autonomous Anti-Overwhelm Agent.
    Ingests unstructured thoughts, calculates cognitive friction,
    and guides the user through atomic 2-minute steps one-at-a-time.
    """

    def __init__(self, model_name: str = "llama3.2:latest", user_name: str = "Mayank"):
        self.user_name = user_name
        self.llm_client = OpenSourceLLMClient(model_name=model_name)
        self.storage = LocalStorage()
        
        # Tools
        self.decomposer_tool = TaskDecomposerTool()
        self.body_doubler_tool = BodyDoublingCompanionTool()
        self.dopamine_tool = DopamineTrackerTool()
        self.exporter_tool = PlanExporterTool()
        
        # Session state
        self.user_state = UserState(user_name=user_name)
        self.current_plan: Optional[DecomposedPlan] = None
        self.session_events: List[Dict[str, Any]] = []

    def deoverwhelm(self, brain_dump: str, paralysis_level: str = "extreme") -> DecomposedPlan:
        """Main agent perception and reasoning cycle."""
        self._log_event("agent_start", {"dump_length": len(brain_dump), "paralysis_level": paralysis_level})
        
        # Generate structured plan via Open-Source AI (Ollama or local engine)
        plan = self.llm_client.generate_plan(brain_dump, paralysis_level)
        self.current_plan = plan
        self.user_state.current_step_index = 0
        self.user_state.completed_step_ids = []
        self.user_state.streak = 0
        
        self._log_event("plan_generated", {
            "total_steps": plan.total_steps,
            "core_blocker": plan.friction_analysis.core_blocker,
            "first_step": plan.first_step_recommendation
        })
        # Persist session to local SQLite
        self.storage.save_session(plan.session_id, self.user_name, brain_dump, plan.model_dump())
        return plan

    def get_current_focus_step(self) -> Optional[AtomicStep]:
        """Anti-paralysis single-step accessor."""
        if not self.current_plan or not self.current_plan.atomic_steps:
            return None
        idx = self.user_state.current_step_index
        if idx < len(self.current_plan.atomic_steps):
            return self.current_plan.atomic_steps[idx]
        return None

    def complete_current_step(self) -> Dict[str, Any]:
        """Mark current step done, trigger dopamine reward, and advance."""
        step = self.get_current_focus_step()
        if not step:
            return {"status": "all_completed", "message": "All atomic steps conquered! Take a well-deserved rest."}

        step.completed = True
        reward = self.dopamine_tool.register_completion(self.user_state, step)
        self.user_state.current_step_index += 1
        
        # Persist step completion
        if self.current_plan:
            self.storage.record_step_completion(
                self.current_plan.session_id,
                self.user_name,
                step.model_dump(),
                reward["points_earned"]
            )
        
        next_step = self.get_current_focus_step()
        encouragement = self.body_doubler_tool.get_message(self.user_state.current_step_index)
        
        self._log_event("step_completed", {
            "step_id": step.id,
            "streak": self.user_state.streak,
            "dopamine": self.user_state.dopamine_score
        })

        return {
            "status": "success",
            "reward": reward,
            "next_step": next_step.model_dump() if next_step else None,
            "encouragement": encouragement,
            "all_done": next_step is None,
            "progress": f"{self.user_state.current_step_index} / {len(self.current_plan.atomic_steps)}"
        }

    def skip_current_step(self) -> Dict[str, Any]:
        """Skip step without guilt."""
        if not self.current_plan:
            return {"status": "no_plan"}
        
        self.user_state.current_step_index += 1
        next_step = self.get_current_focus_step()
        
        self._log_event("step_skipped", {"step_index": self.user_state.current_step_index})
        return {
            "status": "skipped",
            "message": "No guilt. Skipping is valid. Moving to the next pebble.",
            "next_step": next_step.model_dump() if next_step else None,
            "all_done": next_step is None
        }

    def export_plan_markdown(self) -> str:
        """Export current plan as clean Markdown checklist."""
        if not self.current_plan:
            return "No active plan."
        return self.exporter_tool.to_markdown(self.current_plan)

    def _log_event(self, event_type: str, data: Dict[str, Any]):
        self.session_events.append({
            "event": event_type,
            "data": data
        })

    def get_session_history(self) -> List[Dict[str, Any]]:
        """Return history for DevRelay recording."""
        return self.session_events
