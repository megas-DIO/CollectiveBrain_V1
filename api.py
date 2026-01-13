"""REST API Server - CollectiveBrain Multi-Agent System

FastAPI-based REST API for interacting with the CollectiveBrain system.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from collective_brain import CollectiveBrain
from config import get_config, config_to_dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CollectiveBrain API",
    description="Decentralized multi-agent collective brain system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize CollectiveBrain system
config = get_config()
brain = CollectiveBrain(config=config_to_dict(config))


# Request/Response models
class ObjectiveRequest(BaseModel):
    """Request model for processing an objective."""
    objective: str = Field(..., description="The high-level objective to process")
    require_consensus: bool = Field(
        default=True,
        description="Whether to require consensus for finalization"
    )


class ObjectiveResponse(BaseModel):
    """Response model for objective processing."""
    execution_id: str
    task_id: Optional[str] = None
    status: str
    objective: Optional[str] = None
    timestamp: str


class StatusResponse(BaseModel):
    """Response model for system status."""
    orchestrator: Dict[str, Any]
    worker_pool: Dict[str, Any]
    memory: Dict[str, Any]
    consensus_engine: Dict[str, Any]
    supervisor: Dict[str, Any]
    execution_history: int


class VoteRequest(BaseModel):
    """Request model for casting a vote."""
    decision_id: str
    agent_id: str
    vote: str  # "approve", "reject", "abstain"
    justification: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    version: str


# API Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get current system status."""
    try:
        status = brain.get_system_status()
        return status
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/objectives", response_model=ObjectiveResponse)
async def process_objective(request: ObjectiveRequest, background_tasks: BackgroundTasks):
    """
    Process a high-level objective through the CollectiveBrain system.

    This endpoint:
    1. Decomposes the objective into sub-goals
    2. Assigns sub-goals to worker agents
    3. Synthesizes results
    4. Optionally requires consensus for finalization
    """
    try:
        logger.info(f"Received objective: {request.objective}")

        result = brain.process_objective(
            request.objective,
            require_consensus=request.require_consensus
        )

        return ObjectiveResponse(
            execution_id=result["execution_id"],
            task_id=result.get("task_id"),
            status=result["status"],
            objective=result.get("objective"),
            timestamp=result["timestamp"]
        )

    except Exception as e:
        logger.error(f"Error processing objective: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/objectives/{execution_id}")
async def get_objective_result(execution_id: str):
    """Get the full result of a processed objective by execution ID."""
    try:
        history = brain.get_execution_history(limit=100)

        for result in history:
            if result["execution_id"] == execution_id:
                return result

        raise HTTPException(status_code=404, detail="Execution not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting objective result: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_history(limit: int = 10):
    """Get recent execution history."""
    try:
        history = brain.get_execution_history(limit=limit)
        return {
            "total": len(history),
            "limit": limit,
            "executions": history
        }
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/consensus/vote")
async def cast_vote(request: VoteRequest):
    """Cast a vote for a consensus decision."""
    try:
        from consensus_engine import VoteType

        # Map string to VoteType enum
        vote_map = {
            "approve": VoteType.APPROVE,
            "reject": VoteType.REJECT,
            "abstain": VoteType.ABSTAIN
        }

        if request.vote not in vote_map:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid vote type. Must be one of: {list(vote_map.keys())}"
            )

        result = brain.consensus_engine.cast_vote(
            request.decision_id,
            request.agent_id,
            vote_map[request.vote],
            request.justification
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error casting vote: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/consensus/{decision_id}")
async def get_decision_status(decision_id: str):
    """Get the status of a consensus decision."""
    try:
        status = brain.consensus_engine.get_decision_status(decision_id)

        if status is None:
            raise HTTPException(status_code=404, detail="Decision not found")

        return status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting decision status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/consensus/{decision_id}/tally")
async def tally_votes(decision_id: str):
    """Tally votes for a consensus decision."""
    try:
        result = brain.consensus_engine.tally_votes(decision_id)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tallying votes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workers")
async def get_workers():
    """Get status of all worker agents."""
    try:
        return brain.worker_pool.get_pool_status()
    except Exception as e:
        logger.error(f"Error getting workers: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory")
async def get_memory_status():
    """Get status of memory layers."""
    try:
        return brain.memory.get_status()
    except Exception as e:
        logger.error(f"Error getting memory status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
async def get_configuration():
    """Get current system configuration (non-sensitive values only)."""
    try:
        return {
            "environment": config.environment,
            "working_memory_budget": config.memory.working_memory_budget,
            "max_faulty_agents": config.consensus.max_faulty_agents,
            "min_required_agents": brain.consensus_engine.min_required_agents,
            "quality_criteria": {
                "min_workers": config.quality.min_workers,
                "require_consensus": config.quality.require_consensus
            }
        }
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.api.reload,
        log_level=config.api.log_level
    )
