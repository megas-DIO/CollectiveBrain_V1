#!/usr/bin/env python3
"""CollectiveBrain CLI - Multi-Agent Collective Intelligence System

Usage:
    python main.py orchestrate "Build a RAG pipeline"
    python main.py consensus "Deploy to production"
    python main.py status
    python main.py deploy [basic|production] [--execute]
"""

import sys
from orchestrator import Orchestrator
from consensus_engine import DCBFTEngine, VoteType
from memory_layer import UnifiedMemoryLayer
from worker_pool import WorkerPool
from deployment import DeploymentManager


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]
    
    if command == "orchestrate":
        if len(sys.argv) < 3:
            print("Usage: python main.py orchestrate <objective>")
            return
        objective = " ".join(sys.argv[2:])
        orchestrate(objective)
    
    elif command == "consensus":
        if len(sys.argv) < 3:
            print("Usage: python main.py consensus <decision>")
            return
        decision = " ".join(sys.argv[2:])
        run_consensus(decision)
    
    elif command == "status":
        show_status()

    elif command == "deploy":
        mode = "basic"
        execute = False
        for arg in sys.argv[2:]:
            if arg in {"basic", "production"}:
                mode = arg
            elif arg in {"--execute", "--apply"}:
                execute = True
            else:
                print(f"Unknown deploy option: {arg}")
                print("Usage: python main.py deploy [basic|production] [--execute]")
                return
        run_deploy(mode, execute)
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


def orchestrate(objective: str):
    """Decompose an objective into sub-goals and execute with workers."""
    print(f"\n[BRAIN] CollectiveBrain Orchestrator")
    print(f"{'='*50}")
    print(f"Objective: {objective}\n")
    
    orchestrator = Orchestrator()
    pool = WorkerPool()
    memory = UnifiedMemoryLayer()
    
    # Decompose objective
    task = orchestrator.decompose_objective(objective)
    print(f"Task ID: {task['task_id']}")
    print(f"Sub-goals:")
    for i, goal in enumerate(task['sub_goals']):
        print(f"  {i+1}. {goal}")
    
    # Execute each sub-goal with workers
    print(f"\n{'='*50}")
    print("Executing sub-goals...\n")
    
    for i, goal in enumerate(task['sub_goals']):
        role = pool.worker_roles[i % len(pool.worker_roles)]
        result = pool.assign_task(role, task['task_id'], goal)
        
        # Store in memory
        memory.working.add_entry({
            "type": "task_result",
            "task_id": task['task_id'],
            "sub_goal": goal,
            "result": result
        })
        
        print(f"[OK] [{role}] {goal}")
        print(f"  Result: {result['result'][:60]}...")
    
    # Mark complete
    orchestrator.mark_complete(task['task_id'])
    print(f"\n{'='*50}")
    print(f"[DONE] Task completed!")
    print(f"Memory status: {memory.get_status()}")


def run_consensus(decision: str):
    """Run a DCBFT consensus vote on a decision."""
    print(f"\n[VOTE] CollectiveBrain Consensus Engine (DCBFT)")
    print(f"{'='*50}")
    print(f"Decision: {decision}\n")
    
    engine = DCBFTEngine(max_faulty_agents=1)
    agents = ["gemini", "claude", "codex", "grok"]
    
    # Initiate vote
    session = engine.initiate_vote("decision_001", decision, agents)
    print(f"Vote session: {session['decision_id']}")
    print(f"Quorum required: {session['quorum']}/{len(agents)}")
    
    # Simulate votes
    print(f"\n{'='*50}")
    print("Casting votes...\n")
    
    votes = [VoteType.APPROVE, VoteType.APPROVE, VoteType.APPROVE, VoteType.REJECT]
    for agent, vote in zip(agents, votes):
        engine.cast_vote("decision_001", agent, vote, f"{agent} reasoning")
        print(f"  {agent}: {vote.value}")
    
    # Tally
    result = engine.tally_votes("decision_001")
    print(f"\n{'='*50}")
    print(f"Result: {result['decision']}")
    print(f"Vote breakdown: {result['vote_breakdown']}")
    print(f"Consensus: {result['consensus_percentage']}%")


def show_status():
    """Show status of all CollectiveBrain components."""
    print(f"\n[STATUS] CollectiveBrain Status")
    print(f"{'='*50}\n")
    
    pool = WorkerPool()
    memory = UnifiedMemoryLayer()
    
    print("Worker Pool:")
    status = pool.get_pool_status()
    print(f"  Total workers: {status['total_workers']}")
    print(f"  Available: {status['available_workers']}")
    for w in status['workers']:
        print(f"    - {w['role']}: {'Available' if w['is_available'] else 'Busy'}")
    
    print("\nMemory Layers:")
    mem_status = memory.get_status()
    for layer, info in mem_status.items():
        print(f"  {layer}:")
        for k, v in info.items():
            print(f"    {k}: {v}")


def run_deploy(mode: str, execute: bool) -> None:
    """Deploy CollectiveBrain using Docker Compose."""
    manager = DeploymentManager()
    plan = manager.build_plan(mode)
    validation = manager.validate(mode, check_tools=execute)

    print(f"\n[DEPLOY] CollectiveBrain Deployment ({plan.mode})")
    print(f"{'='*50}")
    print(f"Compose file: {plan.compose_file}")
    print("\nPlan:")
    for step in plan.steps:
        print(f"  - {step}")

    if validation["warnings"]:
        print("\nWarnings:")
        for warning in validation["warnings"]:
            print(f"  - {warning}")

    if validation["issues"]:
        print("\nBlocking issues:")
        for issue in validation["issues"]:
            print(f"  - {issue}")
        return

    print(f"\nCommand: {' '.join(plan.command)}")
    if execute:
        result = manager.deploy(mode, execute=True)
        if result["error"]:
            print(f"[ERROR] {result['error']}")
        else:
            print("[OK] Deployment command executed.")
    else:
        print("Dry run complete. Re-run with --execute to apply.")


if __name__ == "__main__":
    main()
