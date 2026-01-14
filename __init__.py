"""
CollectiveBrain - Decentralized Multi-Agent System

A production-ready multi-agent system implementing spec-driven development,
unified memory layers, and Byzantine fault-tolerant consensus protocol (DCBFT).
"""

__version__ = "1.0.0"
__author__ = "CollectiveBrain Contributors"

from collective_brain import CollectiveBrain
from orchestrator import Orchestrator
from worker_pool import WorkerPool, WorkerAgent
from memory_layer import UnifiedMemoryLayer
from consensus_engine import DCBFTEngine, VoteType
from supervisor import Supervisor

__all__ = [
    "CollectiveBrain",
    "Orchestrator",
    "WorkerPool",
    "WorkerAgent",
    "UnifiedMemoryLayer",
    "DCBFTEngine",
    "VoteType",
    "Supervisor",
]
