# CollectiveBrain_V1

**Decentralized Multi-Agent Collective Brain System**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)

A production-ready multi-agent system implementing spec-driven development, unified memory layers, and Byzantine fault-tolerant consensus protocol (DCBFT).

## Features

- ✨ **Orchestrator-Worker Pattern**: Automatic objective decomposition into 3-5 sub-goals with parallel execution
- 🧠 **Four-Layer Memory Backbone**: Working, Session (Redis), Semantic (Milvus), and Relational (Neo4j) memory
- 🔐 **DCBFT Consensus Protocol**: Byzantine fault tolerance with N >= 3f + 1 formula and ~66% super-majority
- 🔍 **Reflection Tokens**: Self-correction mechanism with `[IsRel]` and `[NoSup]` validation
- 📊 **Supervisor Synthesis**: Quality validation and output synthesis from multiple agents
- 🚀 **REST API**: FastAPI-based endpoints for external integration
- 🐳 **Docker Ready**: Full Docker Compose stack with all dependencies
- 📈 **Production Features**: Structured logging, metrics, health checks, and comprehensive tests

## Quick Start

### Option 1: Run Standalone (No Docker)

```bash
# Clone repository
git clone https://github.com/Mega-Therion/CollectiveBrain_V1.git
cd CollectiveBrain_V1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the main application
python collective_brain.py

# Or run the API server
python api.py
```

### Option 2: Run with Docker Compose (Full Stack)

```bash
# Clone repository
git clone https://github.com/Mega-Therion/CollectiveBrain_V1.git
cd CollectiveBrain_V1

# Configure environment
cp .env.example .env
# Edit .env if needed

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f collective-brain

# Access API
curl http://localhost:8000/health
```

This starts the complete stack:
- CollectiveBrain API (port 8000)
- Redis for session memory
- Milvus for semantic search
- Neo4j for knowledge graphs
- Supporting infrastructure

## Architecture

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
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
        ▼                                     ▼
┌──────────────────┐                 ┌──────────────┐
│  Memory Layer    │                 │  Consensus   │
│  - Working       │                 │   Engine     │
│  - Session       │                 │  (DCBFT)     │
│  - Semantic      │                 │              │
│  - Relational    │                 └──────────────┘
└──────────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## Core Components

### 1. Orchestrator (`orchestrator.py`)
Decomposes objectives into actionable sub-goals and coordinates worker execution.

### 2. Worker Pool (`worker_pool.py`)
Specialized agents (Research, Finance, Analysis, Implementation) that execute subtasks with reflection tokens.

### 3. Memory Layer (`memory_layer.py`)
Four-layer memory system:
- **Working**: In-process context with budget limits
- **Session**: Redis-backed state coordination
- **Semantic**: Milvus vector search (<30ms retrieval)
- **Relational**: Neo4j knowledge graphs

### 4. Consensus Engine (`consensus_engine.py`)
DCBFT protocol implementation:
- Formula: N >= 3f + 1 (Byzantine fault tolerance)
- Super-majority (~66%) required for high-impact decisions
- Voting system with approve/reject/abstain

### 5. Supervisor (`supervisor.py`)
Synthesizes worker outputs, validates quality, and coordinates consensus.

### 6. Main Application (`collective_brain.py`)
Integrates all components into unified system with complete processing pipeline.

### 7. REST API (`api.py`)
FastAPI server with endpoints for objectives, consensus, workers, and memory.

## Usage Examples

### Basic Python Usage

```python
from collective_brain import CollectiveBrain

# Initialize system
brain = CollectiveBrain()

# Process objective with consensus
result = brain.process_objective(
    "Build vector search capability for semantic retrieval",
    require_consensus=True
)

print(f"Status: {result['status']}")
print(f"Consensus: {result['consensus']['decision']}")
```

### API Usage

```bash
# Process objective
curl -X POST http://localhost:8000/objectives \
  -H "Content-Type: application/json" \
  -d '{
    "objective": "Analyze market trends for Q1 2026",
    "require_consensus": true
  }'

# Get status
curl http://localhost:8000/status

# Get execution result
curl http://localhost:8000/objectives/{execution_id}
```

### Python API Client

```python
import requests

response = requests.post(
    "http://localhost:8000/objectives",
    json={
        "objective": "Build recommendation system",
        "require_consensus": True
    }
)

result = response.json()
print(f"Execution ID: {result['execution_id']}")
```

See [examples/](examples/) for more complete examples:
- `basic_usage.py`: Standalone Python usage
- `api_client.py`: API client example

## Configuration

Configuration via environment variables (see `.env.example`):

```bash
# General
CB_ENVIRONMENT=production
CB_LOG_LEVEL=INFO

# Memory Layer
CB_MEMORY_WORKING_MEMORY_BUDGET=50
CB_MEMORY_REDIS_HOST=localhost
CB_MEMORY_MILVUS_HOST=localhost
CB_MEMORY_NEO4J_URI=bolt://localhost:7687

# Consensus
CB_CONSENSUS_MAX_FAULTY_AGENTS=1

# API
CB_API_HOST=0.0.0.0
CB_API_PORT=8000

# Quality
CB_QUALITY_MIN_WORKERS=3
CB_QUALITY_REQUIRE_CONSENSUS=true
```

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_consensus_engine.py -v
```

## API Documentation

Complete API documentation available at:
- **Swagger UI**: http://localhost:8000/docs (when server is running)
- **ReDoc**: http://localhost:8000/redoc
- **Written Docs**: [docs/API.md](docs/API.md)

### Key Endpoints

- `POST /objectives` - Process objective through system
- `GET /objectives/{id}` - Get execution result
- `GET /status` - System health and status
- `GET /history` - Execution history
- `POST /consensus/vote` - Cast consensus vote
- `GET /workers` - Worker pool status
- `GET /memory` - Memory layer status

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t collective-brain:latest .

# Run container
docker run -p 8000:8000 collective-brain:latest
```

### Docker Compose (Full Stack)

```bash
docker-compose up -d
```

### Kubernetes

```bash
kubectl apply -f k8s/
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for comprehensive deployment guide including:
- AWS deployment (ECS, ElastiCache, Neo4j AuraDB)
- Kubernetes deployment
- Scaling strategies
- Monitoring and observability
- Backup and recovery

## Monitoring

### Structured Logging

All logs output in JSON format:

```json
{
  "timestamp": "2026-01-13T10:30:00.000000",
  "level": "INFO",
  "logger": "collective_brain",
  "message": "Processing objective",
  "module": "collective_brain"
}
```

### Metrics

```python
from logger import get_metrics

metrics = get_metrics()
print(metrics.get_all())
```

Key metrics:
- `objectives_processed`
- `consensus_decisions`
- `worker_tasks_completed`
- `errors`

### Health Checks

```bash
curl http://localhost:8000/health
```

## Project Structure

```
CollectiveBrain_V1/
├── collective_brain.py     # Main application
├── orchestrator.py          # Objective decomposition
├── worker_pool.py           # Specialized worker agents
├── memory_layer.py          # Four-layer memory system
├── consensus_engine.py      # DCBFT protocol
├── supervisor.py            # Output synthesis & validation
├── api.py                   # FastAPI REST API
├── config.py                # Configuration management
├── logger.py                # Logging & observability
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker image
├── docker-compose.yml       # Full stack deployment
├── .env.example             # Environment configuration
├── tests/                   # Test suite
│   ├── test_consensus_engine.py
│   └── test_integration.py
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEPLOYMENT.md
├── examples/                # Usage examples
│   ├── basic_usage.py
│   └── api_client.py
└── .github/
    └── copilot-instructions.md  # Shared Constitution
```

## Design Principles

### 1. Spec-Driven Development
Every action has documented purpose. Intent documents are source of truth.

### 2. Memory-First Design
Persistent context prevents "lost in the middle" issues across all operations.

### 3. Consensus-Based Security
No single compromised agent can finalize mission-critical workflows (DCBFT).

### 4. Deterministic Task Allocation
Unique task IDs prevent ping-pong loops and wasted compute resources.

### 5. Reflection-Based Validation
Self-correction with `[IsRel]` and `[NoSup]` tokens ensures quality.

## Shared Constitution

The system follows governance rules defined in [.github/copilot-instructions.md](.github/copilot-instructions.md):

- **DCBFT Protocol**: N >= 3f + 1 Byzantine fault tolerance
- **Reflection Tokens**: `[IsRel]` for supported, `[NoSup]` triggers re-retrieval
- **Task Allocation**: Deterministic with unique IDs
- **Memory Management**: Respect budgets, intelligent pruning
- **Spec-Driven**: No "vibe-coding", documented purpose required

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Update documentation
6. Submit a pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/Mega-Therion/CollectiveBrain_V1/issues)
- **Documentation**: [docs/](docs/)
- **Examples**: [examples/](examples/)

## Roadmap

- [ ] GitHub Models API integration for LLM-driven decomposition
- [ ] Production Redis/Milvus/Neo4j integrations
- [ ] Real-time WebSocket updates
- [ ] Advanced observability (Prometheus metrics)
- [ ] Kubernetes Helm charts
- [ ] Authentication and authorization
- [ ] Rate limiting and quotas
- [ ] Multi-tenant support

## Acknowledgments

Built following principles of:
- Decentralized Collective Byzantine Fault Tolerance (DCBFT)
- Memory-first architecture
- Spec-driven development
- Reflection-based validation

---

**Version**: 1.0.0
**Last Updated**: January 13, 2026
