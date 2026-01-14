"""
Basic Usage Example - CollectiveBrain Multi-Agent System

This example demonstrates basic usage of the CollectiveBrain system.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from collective_brain import CollectiveBrain


def main():
    """Run basic CollectiveBrain example."""
    print("=" * 70)
    print("CollectiveBrain - Basic Usage Example")
    print("=" * 70)

    # Initialize the system
    print("\n[1] Initializing CollectiveBrain system...")
    brain = CollectiveBrain()
    print("✓ System initialized successfully")

    # Check initial status
    print("\n[2] Checking system status...")
    status = brain.get_system_status()
    print(f"  - Worker Pool: {status['worker_pool']['total_workers']} workers")
    print(f"  - Available Workers: {status['worker_pool']['available_workers']}")
    print(f"  - Min Required Agents (DCBFT): {status['consensus_engine']['min_required_agents']}")
    print(f"  - Working Memory Budget: {status['memory']['working_memory']['budget']}")

    # Process a simple objective WITHOUT consensus
    print("\n[3] Processing objective (without consensus)...")
    objective1 = "Research the best vector database options for semantic search"

    result1 = brain.process_objective(objective1, require_consensus=False)

    print(f"  Execution ID: {result1['execution_id']}")
    print(f"  Task ID: {result1.get('task_id', 'N/A')}")
    print(f"  Status: {result1['status']}")

    if result1['status'] != 'error':
        print(f"\n  Sub-goals executed:")
        for i, goal in enumerate(result1.get('sub_goals', []), 1):
            print(f"    {i}. {goal}")

        print(f"\n  Workers involved: {result1.get('synthesis', {}).get('total_workers', 0)}")
        print(f"\n  Combined Output:")
        print(f"  {result1.get('synthesis', {}).get('combined_output', 'N/A')}")

    # Process an objective WITH consensus
    print("\n" + "=" * 70)
    print("[4] Processing objective (with consensus)...")
    objective2 = "Design a recommendation system for e-commerce platform"

    result2 = brain.process_objective(objective2, require_consensus=True)

    print(f"  Execution ID: {result2['execution_id']}")
    print(f"  Status: {result2['status']}")

    if result2['status'] != 'error' and 'consensus' in result2:
        consensus = result2['consensus']
        print(f"\n  Consensus Decision: {consensus['decision']}")
        print(f"  Vote Breakdown:")
        print(f"    - Approve: {consensus['vote_breakdown']['approve']}")
        print(f"    - Reject: {consensus['vote_breakdown']['reject']}")
        print(f"    - Abstain: {consensus['vote_breakdown']['abstain']}")
        print(f"  Consensus Percentage: {consensus['consensus_percentage']}%")

    # View execution history
    print("\n" + "=" * 70)
    print("[5] Execution History...")
    history = brain.get_execution_history(limit=5)

    print(f"  Total executions in session: {len(history)}")
    for i, execution in enumerate(history, 1):
        print(f"\n  Execution {i}:")
        print(f"    ID: {execution['execution_id']}")
        print(f"    Objective: {execution.get('objective', 'N/A')}")
        print(f"    Status: {execution['status']}")

    # Final status
    print("\n" + "=" * 70)
    print("[6] Final System Status...")
    final_status = brain.get_system_status()
    print(f"  Total Objectives Processed: {final_status['execution_history']}")
    print(f"  Active Tasks: {final_status['orchestrator']['active_tasks']}")
    print(f"  Completed Tasks: {final_status['orchestrator']['completed_tasks']}")
    print(f"  Documents Indexed: {final_status['memory']['semantic_memory']['indexed_documents']}")
    print(f"  Knowledge Graph Nodes: {final_status['memory']['relational_memory']['nodes']}")

    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
