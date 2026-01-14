"""Test suite for CollectiveBrain V1 components."""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import Orchestrator
from worker_pool import WorkerPool
from memory_layer import UnifiedMemoryLayer, WorkingMemory
from consensus_engine import DCBFTEngine, VoteType
from deployment import DeploymentManager


class TestOrchestrator:
    """Test suite for Orchestrator module."""
    
    def test_create_orchestrator(self):
        """Test orchestrator instantiation."""
        orch = Orchestrator()
        assert orch is not None
        assert len(orch.active_tasks) == 0
        assert len(orch.completed_tasks) == 0
    
    def test_decompose_objective(self):
        """Test objective decomposition into sub-goals."""
        orch = Orchestrator()
        task = orch.decompose_objective("Build a REST API")
        
        assert "task_id" in task
        assert "sub_goals" in task
        assert len(task["sub_goals"]) >= 3
        assert task["status"] == "created"
        assert task["task_id"] in orch.active_tasks
    
    def test_assign_to_worker(self):
        """Test worker assignment."""
        orch = Orchestrator()
        task = orch.decompose_objective("Test objective")
        
        assignment = orch.assign_to_worker(task["task_id"], 0, "Research")
        
        assert assignment["worker_role"] == "Research"
        assert assignment["status"] == "assigned"
        assert "assigned_at" in assignment
    
    def test_mark_complete(self):
        """Test task completion."""
        orch = Orchestrator()
        task = orch.decompose_objective("Complete me")
        task_id = task["task_id"]
        
        assert orch.mark_complete(task_id) is True
        assert task_id not in orch.active_tasks
        assert task_id in orch.completed_tasks
    
    def test_get_task_status(self):
        """Test task status retrieval."""
        orch = Orchestrator()
        task = orch.decompose_objective("Status test")
        
        status = orch.get_task_status(task["task_id"])
        assert status["status"] == "created"
        
        # Test non-existent task
        status = orch.get_task_status("non-existent")
        assert status["status"] == "not_found"


class TestWorkerPool:
    """Test suite for WorkerPool module."""
    
    def test_create_pool(self):
        """Test worker pool instantiation."""
        pool = WorkerPool()
        assert pool is not None
        assert len(pool.worker_roles) > 0
    
    def test_assign_task(self):
        """Test task assignment to worker."""
        pool = WorkerPool()
        result = pool.assign_task("Research", "task-001", "Research AI systems")
        
        assert "result" in result
        assert result["role"] == "Research"
    
    def test_pool_status(self):
        """Test pool status reporting."""
        pool = WorkerPool()
        status = pool.get_pool_status()
        
        assert "total_workers" in status
        assert "available_workers" in status
        assert "workers" in status


class TestMemoryLayer:
    """Test suite for UnifiedMemoryLayer module."""
    
    def test_working_memory(self):
        """Test working memory operations."""
        memory = WorkingMemory()
        
        entry = {"type": "test", "data": "value"}
        memory.add_entry(entry)
        
        assert len(memory.buffer) > 0
    
    def test_unified_memory(self):
        """Test unified memory layer initialization."""
        memory = UnifiedMemoryLayer()
        
        assert memory.working is not None
        assert hasattr(memory, "get_status")
        
        status = memory.get_status()
        assert "working" in status


class TestConsensusEngine:
    """Test suite for DCBFT Consensus Engine."""
    
    def test_create_engine(self):
        """Test consensus engine instantiation."""
        engine = DCBFTEngine(max_faulty_agents=1)
        assert engine is not None
        assert engine.required_agents >= 4  # N >= 3f + 1
    
    def test_initiate_vote(self):
        """Test vote initiation."""
        engine = DCBFTEngine(max_faulty_agents=1)
        agents = ["agent1", "agent2", "agent3", "agent4"]
        
        session = engine.initiate_vote("vote-001", "Test decision", agents)
        
        assert session["decision_id"] == "vote-001"
        assert "quorum" in session
    
    def test_cast_and_tally_votes(self):
        """Test voting and tallying."""
        engine = DCBFTEngine(max_faulty_agents=1)
        agents = ["a1", "a2", "a3", "a4"]
        
        engine.initiate_vote("vote-002", "Approve deployment", agents)
        
        # Cast votes
        engine.cast_vote("vote-002", "a1", VoteType.APPROVE, "Looks good")
        engine.cast_vote("vote-002", "a2", VoteType.APPROVE, "Approved")
        engine.cast_vote("vote-002", "a3", VoteType.APPROVE, "OK")
        engine.cast_vote("vote-002", "a4", VoteType.REJECT, "Not ready")
        
        result = engine.tally_votes("vote-002")
        
        assert result["decision"] in ["approved", "rejected"]
        assert "consensus_percentage" in result


class TestDeployment:
    """Test suite for deployment utilities."""

    def test_build_plan_basic(self):
        manager = DeploymentManager()
        plan = manager.build_plan("basic")

        assert plan.mode == "basic"
        assert "docker" in plan.command[0]
        assert "--profile" not in plan.command

    def test_build_plan_production(self):
        manager = DeploymentManager()
        plan = manager.build_plan("production")

        assert plan.mode == "production"
        assert "--profile" in plan.command

    def test_validate_no_tool_check(self):
        manager = DeploymentManager()
        result = manager.validate("basic", check_tools=False)

        assert "issues" in result
        assert "warnings" in result


class TestIntegration:
    """Integration tests for CollectiveBrain components."""
    
    def test_full_orchestration_flow(self):
        """Test complete orchestration workflow."""
        orch = Orchestrator()
        pool = WorkerPool()
        memory = UnifiedMemoryLayer()
        
        # Decompose objective
        task = orch.decompose_objective("Build vector search")
        
        # Execute sub-goals
        for i, goal in enumerate(task["sub_goals"]):
            role = pool.worker_roles[i % len(pool.worker_roles)]
            result = pool.assign_task(role, task["task_id"], goal)
            
            memory.working.add_entry({
                "task_id": task["task_id"],
                "goal": goal,
                "result": result
            })
        
        # Complete task
        orch.mark_complete(task["task_id"])
        
        assert task["task_id"] in orch.completed_tasks
        assert len(memory.working.buffer) > 0
    
    def test_full_consensus_flow(self):
        """Test complete consensus workflow."""
        engine = DCBFTEngine(max_faulty_agents=1)
        agents = ["gemini", "claude", "codex", "grok"]
        
        # Initiate vote
        session = engine.initiate_vote("deploy-001", "Deploy to production", agents)
        
        # All agents approve
        for agent in agents:
            engine.cast_vote("deploy-001", agent, VoteType.APPROVE, f"{agent} approves")
        
        result = engine.tally_votes("deploy-001")
        
        assert result["decision"] == "approved"
        assert result["consensus_percentage"] == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
