"""CollectiveBrain Main Application - Multi-Agent System

Integrates all modules: Orchestrator, Worker Pool, Memory Layer, Consensus Engine, and Supervisor.
Provides unified interface for decentralized multi-agent collective brain operations.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from orchestrator import Orchestrator
from worker_pool import WorkerPool, WorkerAgent
from memory_layer import UnifiedMemoryLayer
from consensus_engine import DCBFTEngine, VoteType
from supervisor import Supervisor


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CollectiveBrain:
    """Main CollectiveBrain system integrating all components."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the CollectiveBrain system.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or self._default_config()

        # Initialize all subsystems
        logger.info("Initializing CollectiveBrain system...")

        self.orchestrator = Orchestrator()
        self.worker_pool = WorkerPool()
        self.memory = UnifiedMemoryLayer(
            working_budget=self.config.get("working_memory_budget", 50)
        )
        self.consensus_engine = DCBFTEngine(
            max_faulty_agents=self.config.get("max_faulty_agents", 1)
        )
        self.supervisor = Supervisor(consensus_engine=self.consensus_engine)

        self.execution_history: List[Dict] = []

        logger.info("CollectiveBrain system initialized successfully")

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "working_memory_budget": 50,
            "max_faulty_agents": 1,
            "quality_criteria": {
                "min_workers": 3,
                "valid_reflection_tokens": ["[IsRel]"]
            },
            "consensus_required": True
        }

    def process_objective(self, objective: str, require_consensus: bool = True) -> Dict[str, Any]:
        """
        Process a high-level objective through the entire system pipeline.

        Pipeline:
        1. Orchestrator decomposes objective into sub-goals
        2. Worker pool executes each sub-goal
        3. Memory layer tracks context
        4. Supervisor synthesizes results
        5. Consensus engine validates (if required)

        Args:
            objective: The high-level objective to process
            require_consensus: Whether to require consensus for finalization

        Returns:
            Complete execution result
        """
        logger.info(f"Processing objective: {objective}")
        execution_id = f"exec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        try:
            # Step 1: Decompose objective
            logger.info("Step 1: Decomposing objective")
            task = self.orchestrator.decompose_objective(objective)
            task_id = task["task_id"]

            # Log to working memory
            self.memory.working.add_entry({
                "type": "task_created",
                "task_id": task_id,
                "objective": objective,
                "sub_goals": task["sub_goals"]
            })

            # Store in session memory
            self.memory.session.set_session(task_id, task)

            # Index in semantic memory
            self.memory.semantic.index_document(
                task_id,
                f"Objective: {objective}",
                {"type": "task", "status": "in_progress"}
            )

            # Step 2: Execute sub-goals with worker pool
            logger.info("Step 2: Executing sub-goals with worker pool")
            worker_results = []

            for idx, sub_goal in enumerate(task["sub_goals"]):
                # Assign to worker
                worker_role = self._determine_worker_role(sub_goal)
                assignment = self.orchestrator.assign_to_worker(task_id, idx, worker_role)

                # Execute task
                result = self.worker_pool.assign_task(
                    worker_role,
                    task_id,
                    sub_goal
                )

                worker_results.append(result)

                # Log to memory
                self.memory.working.add_entry({
                    "type": "sub_goal_completed",
                    "task_id": task_id,
                    "sub_goal_index": idx,
                    "worker_role": worker_role,
                    "result": result
                })

            # Step 3: Supervisor synthesizes results
            logger.info("Step 3: Synthesizing results")
            synthesis = self.supervisor.synthesize_outputs(task_id, worker_results)

            # Validate quality
            validation = self.supervisor.validate_quality(
                synthesis,
                self.config["quality_criteria"]
            )

            if not validation["passed"]:
                logger.warning(f"Quality validation failed: {validation}")
                return {
                    "execution_id": execution_id,
                    "task_id": task_id,
                    "status": "quality_failed",
                    "validation": validation,
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Step 4: Consensus (if required)
            final_result = {
                "execution_id": execution_id,
                "task_id": task_id,
                "objective": objective,
                "sub_goals": task["sub_goals"],
                "worker_results": worker_results,
                "synthesis": synthesis,
                "validation": validation,
                "timestamp": datetime.utcnow().isoformat()
            }

            if require_consensus and self.config.get("consensus_required", True):
                logger.info("Step 4: Obtaining consensus")

                # Get all available worker agent IDs
                agent_ids = [w.agent_id for w in self.worker_pool.workers.values()]

                # Request consensus
                finalization = self.supervisor.finalize_with_consensus(
                    task_id,
                    synthesis,
                    agent_ids
                )

                # Auto-approve for demonstration (in production, agents would vote)
                if finalization["status"] == "awaiting_consensus":
                    decision_id = finalization["decision_id"]

                    # Simulate agent votes
                    for agent_id in agent_ids[:4]:  # Vote with minimum required
                        self.consensus_engine.cast_vote(
                            decision_id,
                            agent_id,
                            VoteType.APPROVE,
                            "Quality validation passed"
                        )

                    # Tally votes
                    consensus_result = self.consensus_engine.tally_votes(decision_id)
                    final_result["consensus"] = consensus_result

                    if consensus_result["decision"] == "consensus_reached":
                        final_result["status"] = "completed_with_consensus"
                    else:
                        final_result["status"] = "consensus_failed"
                else:
                    final_result["status"] = "consensus_initiation_failed"
                    final_result["consensus_error"] = finalization
            else:
                final_result["status"] = "completed_without_consensus"

            # Mark orchestrator task as complete
            self.orchestrator.mark_complete(task_id)

            # Update memory layers
            self.memory.semantic.index_document(
                f"{task_id}_result",
                synthesis["combined_output"],
                {"type": "result", "status": final_result["status"]}
            )

            # Store execution history
            self.execution_history.append(final_result)

            logger.info(f"Objective processing completed: {final_result['status']}")
            return final_result

        except Exception as e:
            logger.error(f"Error processing objective: {str(e)}", exc_info=True)
            return {
                "execution_id": execution_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def _determine_worker_role(self, sub_goal: str) -> str:
        """
        Determine appropriate worker role for a sub-goal.

        In production, this would use LLM classification.
        For now, use simple keyword matching.
        """
        sub_goal_lower = sub_goal.lower()

        if "research" in sub_goal_lower or "find" in sub_goal_lower:
            return "Research"
        elif "analyze" in sub_goal_lower or "compare" in sub_goal_lower:
            return "Analysis"
        elif "implement" in sub_goal_lower or "build" in sub_goal_lower:
            return "Implementation"
        elif "finance" in sub_goal_lower or "cost" in sub_goal_lower:
            return "Finance"
        else:
            return "Research"  # Default

    def get_system_status(self) -> Dict[str, Any]:
        """Get current status of all system components."""
        return {
            "orchestrator": {
                "active_tasks": len(self.orchestrator.active_tasks),
                "completed_tasks": len(self.orchestrator.completed_tasks)
            },
            "worker_pool": self.worker_pool.get_pool_status(),
            "memory": self.memory.get_status(),
            "consensus_engine": {
                "min_required_agents": self.consensus_engine.min_required_agents,
                "pending_decisions": len(self.consensus_engine.pending_decisions),
                "finalized_decisions": len(self.consensus_engine.finalized_decisions)
            },
            "supervisor": {
                "synthesis_count": len(self.supervisor.synthesis_history)
            },
            "execution_history": len(self.execution_history)
        }

    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        """Get recent execution history."""
        return self.execution_history[-limit:]


def main():
    """Example usage of the CollectiveBrain system."""
    print("=" * 60)
    print("CollectiveBrain Multi-Agent System")
    print("=" * 60)

    # Initialize system
    brain = CollectiveBrain()

    # Display initial status
    print("\n[Initial System Status]")
    status = brain.get_system_status()
    print(f"Worker Pool: {status['worker_pool']['total_workers']} workers")
    print(f"Min Required Agents (DCBFT): {status['consensus_engine']['min_required_agents']}")
    print(f"Working Memory Budget: {status['memory']['working_memory']['budget']}")

    # Process an objective
    print("\n[Processing Objective]")
    objective = "Build vector search capability for semantic document retrieval"

    result = brain.process_objective(objective, require_consensus=True)

    print(f"\nExecution ID: {result['execution_id']}")
    print(f"Task ID: {result.get('task_id', 'N/A')}")
    print(f"Status: {result['status']}")

    if result['status'] != "error":
        print(f"\nSub-goals executed: {len(result.get('sub_goals', []))}")
        print(f"Workers involved: {result.get('synthesis', {}).get('total_workers', 0)}")

        if "consensus" in result:
            consensus = result["consensus"]
            print(f"\nConsensus Decision: {consensus['decision']}")
            print(f"Vote Breakdown: {consensus['vote_breakdown']}")
            print(f"Consensus Percentage: {consensus['consensus_percentage']}%")

        print(f"\n[Synthesized Output]")
        print(result.get('synthesis', {}).get('combined_output', 'N/A'))

    # Display final status
    print("\n" + "=" * 60)
    print("[Final System Status]")
    final_status = brain.get_system_status()
    print(f"Total Executions: {final_status['execution_history']}")
    print(f"Active Tasks: {final_status['orchestrator']['active_tasks']}")
    print(f"Completed Tasks: {final_status['orchestrator']['completed_tasks']}")
    print(f"Documents Indexed: {final_status['memory']['semantic_memory']['indexed_documents']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
