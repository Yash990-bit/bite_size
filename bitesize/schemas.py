"""
Pydantic Schemas for BiteSize: The Open-Source Anti-Overwhelm Agent
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AtomicStep(BaseModel):
    id: str = Field(..., description="Unique step identifier")
    title: str = Field(..., description="The ultra-concrete, unambiguous micro-action")
    description: str = Field(..., description="Low cognitive-load instructions (under 20 words)")
    domain: str = Field(..., description="Category: Physical Space, Academics/Work, Self-Care, Admin")
    estimated_seconds: int = Field(120, description="Target duration (maximum 120s for atomic steps)")
    friction_score: int = Field(..., ge=1, le=5, description="1 (easy) to 5 (heavy psychological resistance)")
    completed: bool = Field(False, description="Completion status")
    micro_reward: str = Field("✨ +10 Dopamine", description="Instant reinforcement message")


class CognitiveFrictionAnalysis(BaseModel):
    perceived_mountain: str = Field(..., description="What the overwhelmed brain is magnifying into an impossibility")
    core_blocker: str = Field(..., description="The single emotional or executive barrier causing freeze")
    paralysis_level: str = Field("Extreme", description="Micro, Extreme, or Gentle")
    identified_domains: List[str] = Field(default_factory=list)


class DecomposedPlan(BaseModel):
    session_id: str
    original_dump: str
    friction_analysis: CognitiveFrictionAnalysis
    first_step_recommendation: str = Field(..., description="The lowest-friction micro-step to break inertia")
    atomic_steps: List[AtomicStep] = Field(default_factory=list)
    body_doubling_message: str = Field(..., description="Compassionate, non-judgmental presence statement")
    total_steps: int = 0
    total_estimated_minutes: float = 0.0


class UserState(BaseModel):
    user_name: str = "Aarav"
    streak: int = 0
    dopamine_score: int = 0
    completed_step_ids: List[str] = Field(default_factory=list)
    current_step_index: int = 0
