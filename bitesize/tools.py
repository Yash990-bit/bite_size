"""
Agent Tools for BiteSize: Autonomous Anti-Overwhelm Toolkit
"""
from typing import Dict, Any, List
from bitesize.schemas import AtomicStep, DecomposedPlan, UserState


class TaskDecomposerTool:
    """Decomposes an overwhelming task into atomic 2-minute steps."""
    name = "task_decomposer"
    description = "Deconstructs a vague, scary task into sub-120-second concrete physical movements."

    def execute(self, task_name: str, domain: str = "General") -> List[AtomicStep]:
        # Atomic decomposition heuristics
        name_lower = task_name.lower()
        if "clean" in name_lower or "room" in name_lower:
            return [
                AtomicStep(
                    id="sub-1",
                    title="Pick up 3 pieces of laundry off the floor",
                    description="Toss them into the hamper. Only 3. Done in 60s.",
                    domain=domain,
                    estimated_seconds=60,
                    friction_score=1,
                    micro_reward="🧺 +10 Laundry Step"
                ),
                AtomicStep(
                    id="sub-2",
                    title="Put 2 empty cups in the sink",
                    description="Carry 2 cups only. Don't wash them yet.",
                    domain=domain,
                    estimated_seconds=45,
                    friction_score=1,
                    micro_reward="☕ +10 Surface Clear"
                )
            ]
        elif "study" in name_lower or "code" in name_lower or "write" in name_lower:
            return [
                AtomicStep(
                    id="sub-1",
                    title="Open the text editor/document and write just the title",
                    description="Zero pressure to write code or body paragraphs.",
                    domain=domain,
                    estimated_seconds=45,
                    friction_score=1,
                    micro_reward="📝 +15 Document Opened"
                ),
                AtomicStep(
                    id="sub-2",
                    title="Write 1 single bullet point or variable name",
                    description="Quality does not matter. Just 1 line on the page.",
                    domain=domain,
                    estimated_seconds=90,
                    friction_score=2,
                    micro_reward="⚡ +20 First Line Written"
                )
            ]
        else:
            return [
                AtomicStep(
                    id="sub-1",
                    title=f"Set a 2-minute timer to examine '{task_name}'",
                    description="Look at the requirements for 120 seconds. You are allowed to stop after.",
                    domain=domain,
                    estimated_seconds=120,
                    friction_score=1,
                    micro_reward="⏱️ +10 Timer Started"
                )
            ]


class BodyDoublingCompanionTool:
    """Provides non-judgmental psychological presence and supportive nudges."""
    name = "body_doubler"
    description = "Dispenses virtual ADHD body-doubling validation and encouragement without toxic positivity."

    MESSAGES = [
        "Hey, executive dysfunction is a neurological glitch, not a character flaw. We tackle this one 2-minute slice at a time.",
        "You do not have to finish the entire project right now. You only have to pick up 3 things.",
        "Remember: Half-done is infinitely better than perfectly unstarted.",
        "I am keeping time for you. Sit back, take one breath, and let's knock out step 1.",
        "Zero guilt. Today's win is simply clicking start."
    ]

    def get_message(self, step_index: int = 0) -> str:
        idx = step_index % len(self.MESSAGES)
        return self.MESSAGES[idx]


class DopamineTrackerTool:
    """Manages streak counting, micro-rewards, and dopamine reinforcement."""
    name = "dopamine_tracker"
    description = "Calculates dopamine momentum and celebration scores upon step completion."

    def register_completion(self, user_state: UserState, step: AtomicStep) -> Dict[str, Any]:
        user_state.completed_step_ids.append(step.id)
        user_state.streak += 1
        points_earned = 15 * user_state.streak
        user_state.dopamine_score += points_earned
        
        milestone = ""
        if user_state.streak == 1:
            milestone = "🚀 Inertia Broken! The hardest part is behind you."
        elif user_state.streak == 3:
            milestone = "🔥 3-Streak on Fire! Your prefrontal cortex is engaged."
        elif user_state.streak >= 5:
            milestone = "👑 Mastery Unlocked! You've conquered 5 atomic blocks."

        return {
            "step_id": step.id,
            "streak": user_state.streak,
            "points_earned": points_earned,
            "total_dopamine": user_state.dopamine_score,
            "milestone": milestone,
            "reward_banner": step.micro_reward
        }


class PlanExporterTool:
    """Formats and exports the de-escalated plan to Markdown or clean text."""
    name = "plan_exporter"
    description = "Exports de-overwhelmed plans into readable Markdown checklists or printable formats."

    def to_markdown(self, plan: DecomposedPlan) -> str:
        lines = [
            f"# 🎯 BiteSize Action Plan for {plan.session_id}",
            f"> *\"{plan.body_doubling_message}\"*\n",
            f"**Perceived Mountain:** {plan.friction_analysis.perceived_mountain}",
            f"**Core Blocker Identified:** {plan.friction_analysis.core_blocker}",
            f"**Total Atomic Steps:** {plan.total_steps} (Est. {plan.total_estimated_minutes} mins total)\n",
            "## ⚡ Atomic 2-Minute Steps\n"
        ]

        for s in plan.atomic_steps:
            check = "[x]" if s.completed else "[ ]"
            lines.append(f"- {check} **{s.title}** ({s.estimated_seconds}s)")
            lines.append(f"  *{s.description}* — `{s.domain}` ({s.micro_reward})")

        lines.append("\n---\n*Generated by BiteSize — Open-Source ADHD Task De-Overwhelmer*")
        return "\n".join(lines)
