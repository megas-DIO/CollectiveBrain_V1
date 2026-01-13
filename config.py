"""Configuration Management - CollectiveBrain Multi-Agent System

Centralized configuration management using environment variables and defaults.
"""

import os
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class MemoryConfig:
    """Memory layer configuration."""
    working_memory_budget: int = 50
    session_memory_enabled: bool = True
    semantic_memory_enabled: bool = True
    relational_memory_enabled: bool = True

    # Redis configuration (Session Memory)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    # Milvus configuration (Semantic Memory)
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    milvus_collection: str = "collective_brain_vectors"
    milvus_dimension: int = 1536  # OpenAI embedding dimension

    # Neo4j configuration (Relational Memory)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: Optional[str] = None


@dataclass
class ConsensusConfig:
    """Consensus engine configuration."""
    max_faulty_agents: int = 1
    consensus_timeout_seconds: int = 300
    auto_vote_enabled: bool = False  # For testing only


@dataclass
class WorkerConfig:
    """Worker pool configuration."""
    default_worker_roles: list = field(default_factory=lambda: [
        "Research", "Finance", "Analysis", "Implementation"
    ])
    workers_per_role: int = 1
    task_timeout_seconds: int = 600


@dataclass
class APIConfig:
    """API server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    workers: int = 1
    log_level: str = "info"


@dataclass
class ModelConfig:
    """AI model configuration for GitHub Models integration."""
    provider: str = "github"  # github, openai, anthropic
    model_name: str = "gpt-4"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7


@dataclass
class QualityConfig:
    """Quality validation configuration."""
    min_workers: int = 3
    valid_reflection_tokens: list = field(default_factory=lambda: ["[IsRel]"])
    require_consensus: bool = True


@dataclass
class CollectiveBrainConfig:
    """Main configuration for CollectiveBrain system."""
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    consensus: ConsensusConfig = field(default_factory=ConsensusConfig)
    worker: WorkerConfig = field(default_factory=WorkerConfig)
    api: APIConfig = field(default_factory=APIConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)

    # General settings
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"


def load_config_from_env() -> CollectiveBrainConfig:
    """
    Load configuration from environment variables.

    Environment variables follow the pattern: CB_{SECTION}_{KEY}
    Example: CB_MEMORY_WORKING_MEMORY_BUDGET=100
    """
    config = CollectiveBrainConfig()

    # Memory configuration
    config.memory.working_memory_budget = int(
        os.getenv("CB_MEMORY_WORKING_MEMORY_BUDGET", "50")
    )
    config.memory.redis_host = os.getenv("CB_MEMORY_REDIS_HOST", "localhost")
    config.memory.redis_port = int(os.getenv("CB_MEMORY_REDIS_PORT", "6379"))
    config.memory.redis_password = os.getenv("CB_MEMORY_REDIS_PASSWORD")

    config.memory.milvus_host = os.getenv("CB_MEMORY_MILVUS_HOST", "localhost")
    config.memory.milvus_port = int(os.getenv("CB_MEMORY_MILVUS_PORT", "19530"))

    config.memory.neo4j_uri = os.getenv("CB_MEMORY_NEO4J_URI", "bolt://localhost:7687")
    config.memory.neo4j_user = os.getenv("CB_MEMORY_NEO4J_USER", "neo4j")
    config.memory.neo4j_password = os.getenv("CB_MEMORY_NEO4J_PASSWORD")

    # Consensus configuration
    config.consensus.max_faulty_agents = int(
        os.getenv("CB_CONSENSUS_MAX_FAULTY_AGENTS", "1")
    )
    config.consensus.auto_vote_enabled = os.getenv(
        "CB_CONSENSUS_AUTO_VOTE_ENABLED", "false"
    ).lower() == "true"

    # Worker configuration
    config.worker.workers_per_role = int(
        os.getenv("CB_WORKER_WORKERS_PER_ROLE", "1")
    )
    config.worker.task_timeout_seconds = int(
        os.getenv("CB_WORKER_TASK_TIMEOUT_SECONDS", "600")
    )

    # API configuration
    config.api.host = os.getenv("CB_API_HOST", "0.0.0.0")
    config.api.port = int(os.getenv("CB_API_PORT", "8000"))
    config.api.reload = os.getenv("CB_API_RELOAD", "false").lower() == "true"
    config.api.workers = int(os.getenv("CB_API_WORKERS", "1"))
    config.api.log_level = os.getenv("CB_API_LOG_LEVEL", "info")

    # Model configuration
    config.model.provider = os.getenv("CB_MODEL_PROVIDER", "github")
    config.model.model_name = os.getenv("CB_MODEL_NAME", "gpt-4")
    config.model.api_key = os.getenv("CB_MODEL_API_KEY")
    config.model.api_base = os.getenv("CB_MODEL_API_BASE")

    # Quality configuration
    config.quality.min_workers = int(os.getenv("CB_QUALITY_MIN_WORKERS", "3"))
    config.quality.require_consensus = os.getenv(
        "CB_QUALITY_REQUIRE_CONSENSUS", "true"
    ).lower() == "true"

    # General settings
    config.environment = os.getenv("CB_ENVIRONMENT", "development")
    config.debug = os.getenv("CB_DEBUG", "false").lower() == "true"
    config.log_level = os.getenv("CB_LOG_LEVEL", "INFO")

    return config


def config_to_dict(config: CollectiveBrainConfig) -> Dict[str, Any]:
    """Convert configuration to dictionary."""
    return {
        "working_memory_budget": config.memory.working_memory_budget,
        "max_faulty_agents": config.consensus.max_faulty_agents,
        "quality_criteria": {
            "min_workers": config.quality.min_workers,
            "valid_reflection_tokens": config.quality.valid_reflection_tokens
        },
        "consensus_required": config.quality.require_consensus,
        "environment": config.environment,
        "debug": config.debug
    }


# Global configuration instance
_config: Optional[CollectiveBrainConfig] = None


def get_config() -> CollectiveBrainConfig:
    """Get or create global configuration instance."""
    global _config
    if _config is None:
        _config = load_config_from_env()
    return _config


if __name__ == "__main__":
    # Example usage
    config = load_config_from_env()

    print("CollectiveBrain Configuration")
    print("=" * 50)
    print(f"\nEnvironment: {config.environment}")
    print(f"Debug Mode: {config.debug}")
    print(f"Log Level: {config.log_level}")

    print(f"\n[Memory Configuration]")
    print(f"Working Memory Budget: {config.memory.working_memory_budget}")
    print(f"Redis: {config.memory.redis_host}:{config.memory.redis_port}")
    print(f"Milvus: {config.memory.milvus_host}:{config.memory.milvus_port}")
    print(f"Neo4j: {config.memory.neo4j_uri}")

    print(f"\n[Consensus Configuration]")
    print(f"Max Faulty Agents: {config.consensus.max_faulty_agents}")
    print(f"Min Required Agents: {(3 * config.consensus.max_faulty_agents) + 1}")

    print(f"\n[Worker Configuration]")
    print(f"Default Roles: {', '.join(config.worker.default_worker_roles)}")
    print(f"Workers per Role: {config.worker.workers_per_role}")

    print(f"\n[API Configuration]")
    print(f"Host: {config.api.host}:{config.api.port}")
    print(f"Workers: {config.api.workers}")

    print(f"\n[Quality Configuration]")
    print(f"Min Workers: {config.quality.min_workers}")
    print(f"Require Consensus: {config.quality.require_consensus}")
