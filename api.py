#!/usr/bin/env python3
"""CollectiveBrain REST API

FastAPI-based REST interface for the CollectiveBrain system.
Provides endpoints for orchestration, consensus, and memory operations.

Usage:
    uvicorn api:app --host 0.0.0.0 --port 8000

Alternatively, run directly:
    python api.py
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime

from orchestrator import Orchestrator
from consensus_engine import DCBFTEngine, VoteType
from memory_layer import UnifiedMemoryLayer
from worker_pool import WorkerPool

app = FastAPI(
    title="CollectiveBrain API",
    description="REST API for the CollectiveBrain multi-agent orchestration system",
    version="1.0.0",
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
orchestrator = Orchestrator()
worker_pool = WorkerPool()
memory = UnifiedMemoryLayer()
consensus_engine = DCBFTEngine(max_faulty_agents=1)

# ============================================================================
# Request/Response Models
# ============================================================================

class OrchestrationRequest(BaseModel):
    objective: str = Field(..., description="The objective to decompose and execute")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context")

class OrchestrationResponse(BaseModel):
    task_id: str
    objective: str
    sub_goals: List[str]
    results: List[Dict[str, Any]]
    status: str
    completed_at: Optional[str] = None

class ConsensusRequest(BaseModel):
    decision_id: Optional[str] = Field(default=None, description="Unique decision ID")
    description: str = Field(..., description="What to vote on")
    agents: Optional[List[str]] = Field(default=None, description="Agents to participate")

class VoteRequest(BaseModel):
    agent: str = Field(..., description="Agent casting the vote")
    vote: str = Field(..., description="approve, reject, or abstain")
    rationale: Optional[str] = Field(default="", description="Reasoning")

class ConsensusResponse(BaseModel):
    decision_id: str
    description: str
    quorum: int
    total_agents: int
    votes: Dict[str, Any]
    decision: Optional[str] = None
    vote_breakdown: Optional[Dict[str, int]] = None
    consensus_percentage: Optional[float] = None

class MemoryEntry(BaseModel):
    content: str = Field(..., description="Memory content")
    tags: Optional[List[str]] = Field(default=None, description="Tags for categorization")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class WorkerStatus(BaseModel):
    role: str
    is_available: bool
    tasks_completed: int

class SystemStatus(BaseModel):
    workers: List[WorkerStatus]
    memory_status: Dict[str, Any]
    active_tasks: int
    consensus_sessions: int

# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"ok": True, "service": "CollectiveBrain", "version": "1.0.0"}

@app.get("/status", response_model=SystemStatus)
async def get_status():
    """Get comprehensive system status."""
    pool_status = worker_pool.get_pool_status()
    mem_status = memory.get_status()
    
    return SystemStatus(
        workers=[
            WorkerStatus(
                role=w["role"],
                is_available=w["is_available"],
                tasks_completed=w.get("tasks_completed", 0)
            )
            for w in pool_status["workers"]
        ],
        memory_status=mem_status,
        active_tasks=len(orchestrator.active_tasks) if hasattr(orchestrator, "active_tasks") else 0,
        consensus_sessions=len(consensus_engine.sessions) if hasattr(consensus_engine, "sessions") else 0,
    )

# ============================================================================
# Orchestration Endpoints
# ============================================================================

@app.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate(request: OrchestrationRequest, background_tasks: BackgroundTasks):
    """
    Decompose an objective into sub-goals and execute with worker agents.
    """
    try:
        # Decompose the objective
        task = orchestrator.decompose_objective(request.objective)
        
        results = []
        for i, goal in enumerate(task["sub_goals"]):
            role = worker_pool.worker_roles[i % len(worker_pool.worker_roles)]
            result = worker_pool.assign_task(role, task["task_id"], goal)
            
            # Store in working memory
            memory.working.add_entry({
                "type": "task_result",
                "task_id": task["task_id"],
                "sub_goal": goal,
                "result": result
            })
            
            results.append({
                "sub_goal": goal,
                "worker": role,
                "result": result["result"],
                "status": result["status"]
            })
        
        # Mark complete
        orchestrator.mark_complete(task["task_id"])
        
        return OrchestrationResponse(
            task_id=task["task_id"],
            objective=request.objective,
            sub_goals=task["sub_goals"],
            results=results,
            status="completed",
            completed_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orchestrate/{task_id}")
async def get_task(task_id: str):
    """Get status of a specific task."""
    if hasattr(orchestrator, "get_task"):
        task = orchestrator.get_task(task_id)
        if task:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

# ============================================================================
# Consensus Endpoints
# ============================================================================

@app.post("/consensus/initiate", response_model=ConsensusResponse)
async def initiate_consensus(request: ConsensusRequest):
    """
    Initiate a new DCBFT consensus vote.
    """
    decision_id = request.decision_id or f"decision_{uuid.uuid4().hex[:8]}"
    agents = request.agents or ["gemini", "claude", "codex", "grok"]
    
    session = consensus_engine.initiate_vote(decision_id, request.description, agents)
    
    return ConsensusResponse(
        decision_id=decision_id,
        description=request.description,
        quorum=session["quorum"],
        total_agents=len(agents),
        votes={},
        decision=None
    )

@app.post("/consensus/{decision_id}/vote")
async def cast_vote(decision_id: str, request: VoteRequest):
    """Cast a vote in an active consensus session."""
    vote_map = {
        "approve": VoteType.APPROVE,
        "reject": VoteType.REJECT,
        "abstain": VoteType.ABSTAIN
    }
    
    vote_type = vote_map.get(request.vote.lower())
    if not vote_type:
        raise HTTPException(status_code=400, detail=f"Invalid vote: {request.vote}")
    
    try:
        consensus_engine.cast_vote(decision_id, request.agent, vote_type, request.rationale)
        return {"ok": True, "agent": request.agent, "vote": request.vote}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/consensus/{decision_id}/tally", response_model=ConsensusResponse)
async def tally_votes(decision_id: str):
    """Tally votes and determine consensus result."""
    try:
        result = consensus_engine.tally_votes(decision_id)
        session = consensus_engine.sessions.get(decision_id, {})
        
        return ConsensusResponse(
            decision_id=decision_id,
            description=session.get("description", ""),
            quorum=session.get("quorum", 0),
            total_agents=len(session.get("agents", [])),
            votes=result.get("votes", {}),
            decision=result["decision"],
            vote_breakdown=result["vote_breakdown"],
            consensus_percentage=result["consensus_percentage"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/consensus/{decision_id}")
async def get_consensus_session(decision_id: str):
    """Get the current state of a consensus session."""
    if hasattr(consensus_engine, "sessions") and decision_id in consensus_engine.sessions:
        return consensus_engine.sessions[decision_id]
    raise HTTPException(status_code=404, detail=f"Consensus session {decision_id} not found")

# ============================================================================
# Memory Endpoints
# ============================================================================

@app.post("/memory/working")
async def add_working_memory(entry: MemoryEntry):
    """Add an entry to working memory."""
    memory.working.add_entry({
        "content": entry.content,
        "tags": entry.tags or [],
        "metadata": entry.metadata or {},
        "timestamp": datetime.utcnow().isoformat()
    })
    return {"ok": True, "layer": "working"}

@app.get("/memory/working")
async def get_working_memory(limit: int = 10):
    """Get recent entries from working memory."""
    entries = memory.working.get_recent(limit) if hasattr(memory.working, "get_recent") else []
    return {"entries": entries, "layer": "working"}

@app.get("/memory/status")
async def get_memory_status():
    """Get status of all memory layers."""
    return memory.get_status()

# ============================================================================
# Worker Pool Endpoints
# ============================================================================

@app.get("/workers")
async def list_workers():
    """List all workers and their status."""
    return worker_pool.get_pool_status()

@app.post("/workers/{role}/task")
async def assign_worker_task(role: str, task: Dict[str, Any]):
    """Directly assign a task to a specific worker role."""
    task_id = task.get("task_id", f"task_{uuid.uuid4().hex[:8]}")
    goal = task.get("goal", "Unspecified task")
    
    try:
        result = worker_pool.assign_task(role, task_id, goal)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# Run the server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
