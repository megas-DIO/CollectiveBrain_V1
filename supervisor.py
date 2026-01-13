"""Supervisor Module - CollectiveBrain Multi-Agent System

Synthesizes worker outputs into coherent final answers and validates consensus.
Follows the Supervisor pattern as defined in the Shared Constitution.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from consensus_engine import DCBFTEngine, VoteType


class Supervisor:
    """Supervisor agent that synthesizes outputs and validates consensus."""

    def __init__(self, consensus_engine: Optional[DCBFTEngine] = None):
        self.consensus_engine = consensus_engine or DCBFTEngine(max_faulty_agents=1)
        self.synthesis_history: List[Dict] = []

    def synthesize_outputs(self, task_id: str, worker_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesize multiple worker outputs into a coherent final answer.

        Args:
            task_id: Unique task identifier
            worker_results: List of worker execution results

        Returns:
            Synthesized output with validation status
        """
        if not worker_results:
            return {
                "task_id": task_id,
                "status": "failed",
                "error": "No worker results to synthesize",
                "timestamp": datetime.utcnow().isoformat()
            }

        # Check for reflection tokens
        unsupported_results = [
            r for r in worker_results
            if r.get("reflection_token") == "[NoSup]"
        ]

        if unsupported_results:
            return {
                "task_id": task_id,
                "status": "needs_reprocessing",
                "message": "Some results lack proper support - triggering re-retrieval",
                "unsupported_count": len(unsupported_results),
                "action_required": "re-retrieve context from Knowledge Graph",
                "timestamp": datetime.utcnow().isoformat()
            }

        # Extract relevant information from worker results
        synthesis = {
            "task_id": task_id,
            "total_workers": len(worker_results),
            "worker_roles": [r.get("role") for r in worker_results],
            "individual_results": [
                {
                    "agent_id": r.get("agent_id"),
                    "role": r.get("role"),
                    "result": r.get("result"),
                    "reflection_token": r.get("reflection_token")
                }
                for r in worker_results
            ],
            "synthesis_timestamp": datetime.utcnow().isoformat()
        }

        # In production, this would use an LLM to synthesize results intelligently
        # For now, combine results into a structured summary
        combined_output = "\n".join([
            f"[{r.get('role')}]: {r.get('result')}"
            for r in worker_results
        ])

        synthesis["combined_output"] = combined_output
        synthesis["status"] = "synthesized"

        self.synthesis_history.append(synthesis)

        return synthesis

    def validate_quality(self, synthesis: Dict[str, Any], quality_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate synthesized output against quality standards.

        Args:
            synthesis: Synthesized output from synthesize_outputs
            quality_criteria: Dictionary of quality requirements

        Returns:
            Validation result
        """
        validation = {
            "task_id": synthesis.get("task_id"),
            "passed": True,
            "checks": {},
            "timestamp": datetime.utcnow().isoformat()
        }

        # Check minimum worker count
        min_workers = quality_criteria.get("min_workers", 1)
        validation["checks"]["min_workers"] = {
            "required": min_workers,
            "actual": synthesis.get("total_workers", 0),
            "passed": synthesis.get("total_workers", 0) >= min_workers
        }

        # Check all reflection tokens are valid
        valid_tokens = quality_criteria.get("valid_reflection_tokens", ["[IsRel]"])
        all_tokens_valid = all(
            r.get("reflection_token") in valid_tokens
            for r in synthesis.get("individual_results", [])
        )
        validation["checks"]["reflection_tokens"] = {
            "required": valid_tokens,
            "passed": all_tokens_valid
        }

        # Overall validation status
        validation["passed"] = all(
            check["passed"] for check in validation["checks"].values()
        )

        return validation

    def request_consensus(self, decision_id: str, description: str, agent_ids: List[str]) -> Dict[str, Any]:
        """
        Request consensus for a high-impact decision.

        Args:
            decision_id: Unique decision identifier
            description: Description of the decision
            agent_ids: List of agent IDs to participate in voting

        Returns:
            Consensus vote session details
        """
        return self.consensus_engine.initiate_vote(decision_id, description, agent_ids)

    def finalize_with_consensus(self, task_id: str, synthesis: Dict[str, Any], agent_ids: List[str]) -> Dict[str, Any]:
        """
        Finalize a synthesis after obtaining consensus from agents.

        Args:
            task_id: Task identifier
            synthesis: Synthesized output
            agent_ids: Agent IDs for consensus voting

        Returns:
            Finalization result with consensus status
        """
        decision_id = f"finalize_{task_id}"

        # Initiate consensus vote
        vote_session = self.consensus_engine.initiate_vote(
            decision_id,
            f"Finalize synthesis for task {task_id}",
            agent_ids
        )

        if "error" in vote_session:
            return {
                "task_id": task_id,
                "status": "consensus_failed",
                "error": vote_session["error"],
                "timestamp": datetime.utcnow().isoformat()
            }

        return {
            "task_id": task_id,
            "decision_id": decision_id,
            "status": "awaiting_consensus",
            "vote_session": vote_session,
            "synthesis": synthesis,
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_synthesis_history(self, task_id: Optional[str] = None) -> List[Dict]:
        """
        Get synthesis history, optionally filtered by task_id.

        Args:
            task_id: Optional task ID to filter by

        Returns:
            List of synthesis records
        """
        if task_id:
            return [s for s in self.synthesis_history if s.get("task_id") == task_id]
        return self.synthesis_history


if __name__ == "__main__":
    # Example usage
    from worker_pool import WorkerPool

    print("=== Supervisor Agent Example ===")

    supervisor = Supervisor()

    # Simulate worker results
    worker_results = [
        {
            "task_id": "task_001",
            "agent_id": "agent_1",
            "role": "Research",
            "result": "Found 3 vector database options: Milvus, Pinecone, Weaviate",
            "reflection_token": "[IsRel]"
        },
        {
            "task_id": "task_001",
            "agent_id": "agent_2",
            "role": "Analysis",
            "result": "Milvus offers best performance for our use case with HNSW index",
            "reflection_token": "[IsRel]"
        },
        {
            "task_id": "task_001",
            "agent_id": "agent_3",
            "role": "Implementation",
            "result": "Can integrate Milvus Lite with <30ms retrieval latency",
            "reflection_token": "[IsRel]"
        }
    ]

    # Synthesize outputs
    synthesis = supervisor.synthesize_outputs("task_001", worker_results)
    print(f"\nSynthesis Status: {synthesis['status']}")
    print(f"Workers involved: {synthesis['total_workers']}")
    print(f"\nCombined Output:\n{synthesis['combined_output']}")

    # Validate quality
    quality_criteria = {
        "min_workers": 3,
        "valid_reflection_tokens": ["[IsRel]"]
    }
    validation = supervisor.validate_quality(synthesis, quality_criteria)
    print(f"\nQuality Validation: {'PASSED' if validation['passed'] else 'FAILED'}")

    # Request consensus for finalization
    agent_ids = ["agent_1", "agent_2", "agent_3", "agent_4"]
    finalization = supervisor.finalize_with_consensus("task_001", synthesis, agent_ids)
    print(f"\nFinalization Status: {finalization['status']}")
    print(f"Consensus Decision ID: {finalization.get('decision_id')}")
