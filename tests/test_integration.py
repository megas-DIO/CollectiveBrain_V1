"""Integration tests for CollectiveBrain system."""

import pytest
from collective_brain import CollectiveBrain
from config import CollectiveBrainConfig, MemoryConfig, ConsensusConfig, QualityConfig


class TestCollectiveBrainIntegration:
    """Integration tests for the full CollectiveBrain system."""

    def test_system_initialization(self):
        """Test system initialization with all components."""
        brain = CollectiveBrain()

        assert brain.orchestrator is not None
        assert brain.worker_pool is not None
        assert brain.memory is not None
        assert brain.consensus_engine is not None
        assert brain.supervisor is not None

    def test_get_system_status(self):
        """Test system status retrieval."""
        brain = CollectiveBrain()
        status = brain.get_system_status()

        assert "orchestrator" in status
        assert "worker_pool" in status
        assert "memory" in status
        assert "consensus_engine" in status
        assert "supervisor" in status

        # Verify worker pool initialized
        assert status["worker_pool"]["total_workers"] > 0

    def test_process_objective_complete_pipeline(self):
        """Test complete objective processing pipeline."""
        brain = CollectiveBrain()

        objective = "Build vector search capability"
        result = brain.process_objective(objective, require_consensus=True)

        # Verify execution completed
        assert result["status"] in [
            "completed_with_consensus",
            "completed_without_consensus",
            "quality_failed",
            "consensus_failed"
        ]

        # Verify structure
        if result["status"] != "error":
            assert "task_id" in result
            assert "objective" in result
            assert result["objective"] == objective
            assert "sub_goals" in result
            assert "worker_results" in result
            assert "synthesis" in result

    def test_process_objective_without_consensus(self):
        """Test objective processing without consensus requirement."""
        brain = CollectiveBrain()

        objective = "Analyze market trends"
        result = brain.process_objective(objective, require_consensus=False)

        assert result["status"] == "completed_without_consensus"
        assert "consensus" not in result or result.get("consensus") is None

    def test_worker_role_determination(self):
        """Test worker role determination logic."""
        brain = CollectiveBrain()

        assert brain._determine_worker_role("Research vector databases") == "Research"
        assert brain._determine_worker_role("Analyze performance metrics") == "Analysis"
        assert brain._determine_worker_role("Implement new feature") == "Implementation"
        assert brain._determine_worker_role("Calculate costs") == "Finance"
        assert brain._determine_worker_role("Random task") == "Research"  # Default

    def test_memory_integration(self):
        """Test memory layer integration during processing."""
        brain = CollectiveBrain()

        initial_memory_status = brain.memory.get_status()
        initial_size = initial_memory_status["working_memory"]["size"]

        objective = "Test memory integration"
        brain.process_objective(objective, require_consensus=False)

        final_memory_status = brain.memory.get_status()
        final_size = final_memory_status["working_memory"]["size"]

        # Verify memory was used
        assert final_size > initial_size
        assert final_memory_status["semantic_memory"]["indexed_documents"] > 0

    def test_execution_history(self):
        """Test execution history tracking."""
        brain = CollectiveBrain()

        # Process multiple objectives
        brain.process_objective("First objective", require_consensus=False)
        brain.process_objective("Second objective", require_consensus=False)

        history = brain.get_execution_history()

        assert len(history) == 2
        assert history[0]["objective"] == "First objective"
        assert history[1]["objective"] == "Second objective"

    def test_execution_history_limit(self):
        """Test execution history with limit."""
        brain = CollectiveBrain()

        # Process 5 objectives
        for i in range(5):
            brain.process_objective(f"Objective {i}", require_consensus=False)

        # Get last 3
        history = brain.get_execution_history(limit=3)

        assert len(history) == 3
        assert history[-1]["objective"] == "Objective 4"

    def test_custom_config(self):
        """Test system initialization with custom configuration."""
        custom_config = {
            "working_memory_budget": 100,
            "max_faulty_agents": 2,
            "quality_criteria": {
                "min_workers": 2,
                "valid_reflection_tokens": ["[IsRel]"]
            },
            "consensus_required": False
        }

        brain = CollectiveBrain(config=custom_config)

        assert brain.memory.working.budget == 100
        assert brain.consensus_engine.max_faulty_agents == 2
        assert brain.consensus_engine.min_required_agents == 7  # 3*2 + 1

    def test_quality_validation_failure(self):
        """Test handling of quality validation failure."""
        config = {
            "quality_criteria": {
                "min_workers": 10,  # Impossible to meet with default workers
                "valid_reflection_tokens": ["[IsRel]"]
            }
        }

        brain = CollectiveBrain(config=config)
        result = brain.process_objective("Test objective", require_consensus=False)

        # Should fail quality validation
        assert result["status"] == "quality_failed"
        assert "validation" in result
        assert result["validation"]["passed"] is False

    def test_multiple_concurrent_tasks(self):
        """Test handling of multiple tasks."""
        brain = CollectiveBrain()

        # Process multiple objectives
        results = []
        for i in range(3):
            result = brain.process_objective(
                f"Concurrent task {i}",
                require_consensus=False
            )
            results.append(result)

        # Verify all completed
        assert len(results) == 3
        for result in results:
            assert result["status"] in [
                "completed_without_consensus",
                "quality_failed"
            ]

        # Verify unique task IDs
        task_ids = [r["task_id"] for r in results]
        assert len(set(task_ids)) == 3

    def test_consensus_integration(self):
        """Test consensus engine integration in full pipeline."""
        brain = CollectiveBrain()

        result = brain.process_objective(
            "Deploy critical update",
            require_consensus=True
        )

        # Verify consensus was attempted
        if result["status"] == "completed_with_consensus":
            assert "consensus" in result
            consensus = result["consensus"]
            assert "decision" in consensus
            assert "vote_breakdown" in consensus
            assert "consensus_percentage" in consensus


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
