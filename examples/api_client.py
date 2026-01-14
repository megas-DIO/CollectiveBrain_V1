"""
API Client Example - CollectiveBrain Multi-Agent System

This example demonstrates how to interact with the CollectiveBrain API.

Note: This requires the API server to be running.
Start the server with: python api.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports (if needed)
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import time
from typing import Dict, Any


class CollectiveBrainClient:
    """Client for interacting with CollectiveBrain API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client.

        Args:
            base_url: Base URL of the CollectiveBrain API
        """
        self.base_url = base_url.rstrip('/')

    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        response = requests.get(f"{self.base_url}/status")
        response.raise_for_status()
        return response.json()

    def process_objective(
        self,
        objective: str,
        require_consensus: bool = True
    ) -> Dict[str, Any]:
        """
        Process an objective.

        Args:
            objective: The objective to process
            require_consensus: Whether to require consensus

        Returns:
            Objective response
        """
        response = requests.post(
            f"{self.base_url}/objectives",
            json={
                "objective": objective,
                "require_consensus": require_consensus
            }
        )
        response.raise_for_status()
        return response.json()

    def get_objective_result(self, execution_id: str) -> Dict[str, Any]:
        """
        Get full objective result.

        Args:
            execution_id: Execution ID

        Returns:
            Full execution result
        """
        response = requests.get(f"{self.base_url}/objectives/{execution_id}")
        response.raise_for_status()
        return response.json()

    def get_history(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get execution history.

        Args:
            limit: Maximum number of executions to return

        Returns:
            Execution history
        """
        response = requests.get(f"{self.base_url}/history?limit={limit}")
        response.raise_for_status()
        return response.json()

    def cast_vote(
        self,
        decision_id: str,
        agent_id: str,
        vote: str,
        justification: str = None
    ) -> Dict[str, Any]:
        """
        Cast a consensus vote.

        Args:
            decision_id: Decision ID
            agent_id: Agent ID
            vote: Vote type (approve, reject, abstain)
            justification: Optional vote justification

        Returns:
            Vote confirmation
        """
        response = requests.post(
            f"{self.base_url}/consensus/vote",
            json={
                "decision_id": decision_id,
                "agent_id": agent_id,
                "vote": vote,
                "justification": justification
            }
        )
        response.raise_for_status()
        return response.json()

    def get_decision_status(self, decision_id: str) -> Dict[str, Any]:
        """
        Get consensus decision status.

        Args:
            decision_id: Decision ID

        Returns:
            Decision status
        """
        response = requests.get(f"{self.base_url}/consensus/{decision_id}")
        response.raise_for_status()
        return response.json()

    def get_workers(self) -> Dict[str, Any]:
        """Get worker pool status."""
        response = requests.get(f"{self.base_url}/workers")
        response.raise_for_status()
        return response.json()

    def get_memory_status(self) -> Dict[str, Any]:
        """Get memory layer status."""
        response = requests.get(f"{self.base_url}/memory")
        response.raise_for_status()
        return response.json()


def main():
    """Run API client example."""
    print("=" * 70)
    print("CollectiveBrain - API Client Example")
    print("=" * 70)

    # Initialize client
    client = CollectiveBrainClient("http://localhost:8000")

    # Health check
    print("\n[1] Health Check...")
    try:
        health = client.health_check()
        print(f"  Status: {health['status']}")
        print(f"  Version: {health['version']}")
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error: {e}")
        print("  Make sure the API server is running: python api.py")
        return

    # Get system status
    print("\n[2] System Status...")
    status = client.get_status()
    print(f"  Total Workers: {status['worker_pool']['total_workers']}")
    print(f"  Available Workers: {status['worker_pool']['available_workers']}")
    print(f"  Active Tasks: {status['orchestrator']['active_tasks']}")

    # Process objective
    print("\n[3] Processing Objective...")
    objective = "Analyze market trends for Q1 2026"
    print(f"  Objective: {objective}")

    result = client.process_objective(objective, require_consensus=True)
    print(f"  Execution ID: {result['execution_id']}")
    print(f"  Task ID: {result.get('task_id')}")
    print(f"  Status: {result['status']}")

    # Get full result
    print("\n[4] Fetching Full Result...")
    time.sleep(1)  # Brief pause
    full_result = client.get_objective_result(result['execution_id'])

    if 'synthesis' in full_result:
        print(f"  Workers Involved: {full_result['synthesis']['total_workers']}")
        print(f"  Worker Roles: {', '.join(full_result['synthesis']['worker_roles'])}")

    if 'consensus' in full_result:
        consensus = full_result['consensus']
        print(f"\n  Consensus Decision: {consensus['decision']}")
        print(f"  Vote Breakdown: {consensus['vote_breakdown']}")

    # Get execution history
    print("\n[5] Execution History...")
    history = client.get_history(limit=5)
    print(f"  Total Executions: {history['total']}")

    for i, execution in enumerate(history['executions'][:3], 1):
        print(f"\n  Execution {i}:")
        print(f"    ID: {execution['execution_id']}")
        print(f"    Status: {execution['status']}")

    # Get worker status
    print("\n[6] Worker Pool Status...")
    workers = client.get_workers()
    print(f"  Total Workers: {workers['total_workers']}")
    print(f"  Available: {workers['available_workers']}")

    print("\n  Worker Details:")
    for worker in workers['workers'][:4]:
        status_icon = "✓" if worker['is_available'] else "✗"
        print(f"    {status_icon} {worker['role']} - Completed: {worker['tasks_completed']}")

    # Get memory status
    print("\n[7] Memory Layer Status...")
    memory = client.get_memory_status()
    print(f"  Working Memory: {memory['working_memory']['size']}/{memory['working_memory']['budget']}")
    print(f"  Active Sessions: {memory['session_memory']['active_sessions']}")
    print(f"  Indexed Documents: {memory['semantic_memory']['indexed_documents']}")
    print(f"  Knowledge Graph Nodes: {memory['relational_memory']['nodes']}")

    print("\n" + "=" * 70)
    print("API Client Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
