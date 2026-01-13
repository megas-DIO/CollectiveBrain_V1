# CollectiveBrain Architecture

## Overview

CollectiveBrain is a decentralized multi-agent collective intelligence system that implements:

- **Spec-Driven Development**: Intent documents as source of truth
- **Unified Memory Layer**: Four-layer memory backbone (Working, Session, Semantic, Relational)
- **DCBFT Consensus Protocol**: Byzantine fault tolerance with N >= 3f + 1 formula
- **Orchestrator-Worker Pattern**: Decomposition and parallel execution
- **Reflection Tokens**: Self-correction and validation

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CollectiveBrain                         │
│                    Main Application                         │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Orchestrator │  │ Worker Pool  │  │  Supervisor  │
│              │  │              │  │              │
│ - Decompose  │  │ - Research   │  │ - Synthesize │
│ - Assign     │  │ - Finance    │  │ - Validate   │
│ - Monitor    │  │ - Analysis   │  │ - Quality    │
└──────────────┘  │ - Implement  │  └──────────────┘
                  └──────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
        ▼                                     ▼
┌──────────────────┐                 ┌──────────────┐
│  Memory Layer    │                 │  Consensus   │
│                  │                 │   Engine     │
│ - Working Memory │                 │              │
│ - Session (Redis)│                 │ - DCBFT      │
│ - Semantic (Milvus)                │ - Voting     │
│ - Relational (Neo4j)               │ - Quorum     │
└──────────────────┘                 └──────────────┘
```

## Core Components

### 1. Orchestrator (`orchestrator.py`)

**Responsibilities:**
- Decompose high-level objectives into 3-5 sub-goals
- Assign sub-goals to appropriate worker agents
- Track task progress and completion
- Maintain deterministic task allocation

**Key Methods:**
- `decompose_objective(objective)`: Break down objective into actionable sub-goals
- `assign_to_worker(task_id, sub_goal_index, worker_role)`: Assign work to specialized agents
- `get_task_status(task_id)`: Monitor task progress

### 2. Worker Pool (`worker_pool.py`)

**Responsibilities:**
- Execute assigned subtasks within specialized roles
- Implement reflection tokens for self-correction
- Report structured outputs with validation

**Worker Roles:**
- **Research**: Information gathering and analysis
- **Finance**: Cost analysis and financial projections
- **Analysis**: Data analysis and pattern recognition
- **Implementation**: Code generation and system building

**Key Methods:**
- `execute_task(task_id, instruction)`: Execute a subtask
- `get_available_worker(role)`: Find available worker by role
- `assign_task(role, task_id, instruction)`: Route task to worker

### 3. Memory Layer (`memory_layer.py`)

Four-layer memory architecture for comprehensive context management:

#### Working Memory
- **Type**: In-process deque with budget limits
- **Purpose**: Active context for current operations
- **Budget**: Configurable (default: 50 entries)
- **Behavior**: Auto-prunes oldest entries when full

#### Session Memory
- **Backend**: Redis (sub-millisecond coordination)
- **Purpose**: Live task state synchronization
- **Use Cases**: Cross-agent coordination, distributed state

#### Semantic Memory
- **Backend**: Milvus Lite with HNSW index
- **Purpose**: Vector-based semantic retrieval
- **Performance**: Sub-30ms retrieval latency
- **Use Cases**: Document search, knowledge retrieval

#### Relational Memory
- **Backend**: Neo4j AuraDB
- **Purpose**: Knowledge graph for multi-hop reasoning
- **Use Cases**: Entity relationships, causal chains

### 4. Consensus Engine (`consensus_engine.py`)

**DCBFT Protocol Implementation:**

**Formula**: `N >= 3f + 1`
- N = total number of agents
- f = maximum faulty/Byzantine agents

**Quorum**: ~66% super-majority required

**Vote Types:**
- `APPROVE`: Support the decision
- `REJECT`: Oppose the decision
- `ABSTAIN`: Neutral stance

**Decision Outcomes:**
- `CONSENSUS_REACHED`: Super-majority approval
- `CONSENSUS_FAILED`: Super-majority rejection or split
- `INSUFFICIENT_VOTES`: Quorum not met
- `BYZANTINE_DETECTED`: Malicious behavior identified

**Key Methods:**
- `initiate_vote(decision_id, description, required_agents)`: Start consensus process
- `cast_vote(decision_id, agent_id, vote)`: Record agent vote
- `tally_votes(decision_id)`: Determine consensus outcome

### 5. Supervisor (`supervisor.py`)

**Responsibilities:**
- Synthesize multiple worker outputs into coherent results
- Validate quality standards before finalization
- Coordinate consensus for high-impact decisions
- Trigger re-retrieval when `[NoSup]` tokens detected

**Key Methods:**
- `synthesize_outputs(task_id, worker_results)`: Combine worker results
- `validate_quality(synthesis, quality_criteria)`: Ensure quality standards
- `finalize_with_consensus(task_id, synthesis, agent_ids)`: Require consensus approval

### 6. Main Application (`collective_brain.py`)

**Unified System Integration:**

**Pipeline:**
1. **Decomposition**: Orchestrator breaks down objective
2. **Execution**: Worker pool executes sub-goals in parallel
3. **Memory Tracking**: All states logged to memory layers
4. **Synthesis**: Supervisor combines results
5. **Validation**: Quality checks performed
6. **Consensus**: High-impact decisions require approval

**Key Methods:**
- `process_objective(objective, require_consensus)`: Full pipeline execution
- `get_system_status()`: Comprehensive system health check

## Reflection Tokens

Self-correction mechanism for quality assurance:

- `[IsRel]`: Information is relevant and supported by context
- `[NoSup]`: No support found in context - triggers re-retrieval

**Workflow:**
1. Worker generates output with reflection token
2. Supervisor checks tokens during synthesis
3. If `[NoSup]` detected, system automatically re-retrieves context from Knowledge Graph
4. Re-processed result replaces unsupported output

## Configuration (`config.py`)

Centralized configuration management with environment variables:

**Configuration Sections:**
- **MemoryConfig**: Memory layer settings
- **ConsensusConfig**: DCBFT parameters
- **WorkerConfig**: Worker pool settings
- **APIConfig**: API server configuration
- **ModelConfig**: AI model integration
- **QualityConfig**: Validation criteria

**Environment Variable Pattern**: `CB_{SECTION}_{KEY}`

Example: `CB_MEMORY_WORKING_MEMORY_BUDGET=100`

## API Layer (`api.py`)

FastAPI-based REST API for system interaction:

**Endpoints:**
- `POST /objectives`: Process a new objective
- `GET /objectives/{id}`: Get execution result
- `GET /status`: System status
- `GET /history`: Execution history
- `POST /consensus/vote`: Cast consensus vote
- `GET /consensus/{id}`: Get decision status
- `GET /workers`: Worker pool status
- `GET /memory`: Memory layer status

## Deployment Architecture

### Docker Compose Stack

```yaml
Services:
  - collective-brain: Main application (Python)
  - redis: Session memory (Redis 7)
  - milvus: Semantic memory (Milvus + HNSW)
  - neo4j: Relational memory (Neo4j 5)
  - etcd: Milvus coordination
  - minio: Milvus object storage
```

### Production Considerations

1. **Scalability**: Horizontal scaling via multiple API instances
2. **High Availability**: Redis Sentinel, Neo4j cluster, Milvus distributed
3. **Security**: TLS/SSL, authentication, network isolation
4. **Monitoring**: Prometheus metrics, structured logging
5. **Backup**: Regular backups of Neo4j and Milvus data

## Design Principles

### 1. Spec-Driven Development
Every action must have documented purpose and clear intent.

### 2. Memory-First Design
Persistent context across all operations prevents "lost in the middle" issues.

### 3. Consensus-Based Security
No single compromised agent can finalize mission-critical workflows.

### 4. Deterministic Task Allocation
Unique task IDs prevent ping-pong loops and wasted compute.

### 5. Reflection-Based Validation
Self-correction mechanisms ensure output quality and relevance.

## Extension Points

### Adding New Worker Roles

```python
# In worker_pool.py
class WorkerPool:
    def __init__(self):
        self.worker_roles = [
            "Research",
            "Finance",
            "Analysis",
            "Implementation",
            "YourNewRole"  # Add here
        ]
```

### Custom Memory Backends

Implement interfaces defined in `memory_layer.py`:
- `WorkingMemory`
- `SessionMemory`
- `SemanticMemory`
- `RelationalMemory`

### AI Model Integration

Update `config.py` with model provider settings and integrate in worker execution logic.

## References

- [Shared Constitution](.github/copilot-instructions.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
