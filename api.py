"""
FastAPI Server connecting the BiteSize Python Agent to the Web UI.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from bitesize.agent import BiteSizeAgent
from bitesize.schemas import DecomposedPlan

app = FastAPI(
    title="BiteSize Agent API",
    description="Open-Source ADHD Anti-Overwhelm Agent Backend",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global active agent instance
active_agent = BiteSizeAgent()


class DeoverwhelmRequest(BaseModel):
    brain_dump: str
    paralysis_level: Optional[str] = "extreme"
    model_name: Optional[str] = "llama3.2:latest"
    user_name: Optional[str] = "Mayank"


class StepActionRequest(BaseModel):
    step_id: Optional[str] = None


@app.get("/api/health")
def health_check():
    ollama_online = active_agent.llm_client.is_ollama_available()
    models = active_agent.llm_client.list_local_models() if ollama_online else []
    return {
        "status": "healthy",
        "agent": "BiteSize v1.0",
        "ollama_connected": ollama_online,
        "available_models": models,
        "engine_mode": "Ollama Open Weights" if ollama_online else "Embedded Local Neural Engine"
    }


@app.post("/api/deoverwhelm", response_model=DecomposedPlan)
def deoverwhelm_endpoint(req: DeoverwhelmRequest):
    if not req.brain_dump.strip():
        raise HTTPException(status_code=400, detail="Brain dump cannot be empty")
    
    if req.model_name != active_agent.llm_client.model_name:
        active_agent.llm_client.model_name = req.model_name
    
    plan = active_agent.deoverwhelm(req.brain_dump, paralysis_level=req.paralysis_level)
    return plan


@app.get("/api/focus-step")
def get_focus_step():
    step = active_agent.get_current_focus_step()
    if not step:
        return {"status": "empty", "step": None}
    return {
        "status": "active",
        "step": step.model_dump(),
        "step_index": active_agent.user_state.current_step_index + 1,
        "total_steps": len(active_agent.current_plan.atomic_steps) if active_agent.current_plan else 0,
        "streak": active_agent.user_state.streak,
        "dopamine": active_agent.user_state.dopamine_score
    }


@app.post("/api/complete-step")
def complete_step_endpoint(req: StepActionRequest):
    result = active_agent.complete_current_step()
    return result


@app.post("/api/skip-step")
def skip_step_endpoint():
    result = active_agent.skip_current_step()
    return result


@app.get("/api/export-markdown")
def export_markdown_endpoint():
    md = active_agent.export_plan_markdown()
    return {"markdown": md}


# Mount the web frontend at root
app.mount("/", StaticFiles(directory="web", html=True), name="static")
