# CollectiveBrain V1

[![CI/CD](https://github.com/Mega-Therion/CollectiveBrain_V1/actions/workflows/ci.yml/badge.svg)](https://github.com/Mega-Therion/CollectiveBrain_V1/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Decentralized multi-agent collective brain system implementing spec-driven development, unified memory layer, and DCBFT consensus protocol.

## 🧠 Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                      Orchestrator                            │
│  Decomposes objectives → 3-5 sub-goals → Assigns to workers │
│              (LLM-powered with GitHub Models)                │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   Worker:     │     │   Worker:     │     │   Worker:     │
│   Research    │     │   Finance     │     │   Analysis    │
└───────────────┘     └───────────────┘     └───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Unified Memory Layer                       │
│  Working │ Session (Redis) │ Semantic (Milvus) │ Relational │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     DCBFT Consensus                          │
│  N >= 3f + 1  │  Byzantine Fault Tolerant  │  66% Quorum    │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Mega-Therion/CollectiveBrain_V1.git
cd CollectiveBrain_V1

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### Basic Usage

```bash
# Run orchestration (decomposes objective into sub-goals)
python main.py orchestrate "Build a vector search capability"

# Run consensus vote
python main.py consensus "Deploy to production"

# Preview deployment plan (dry run)
python main.py deploy basic

# Execute deployment with production profile
python main.py deploy production --execute

# Check system status
python main.py status
```

### Docker Deployment

```bash
# Basic mode (local only)
docker-compose up brain

# Production mode (with Redis + Milvus)
docker-compose --profile production up -d
```

## 📦 Modules

| Module | Description |
| ------ | ----------- |
| `orchestrator.py` | Decomposes objectives into sub-goals using LLM |
| `worker_pool.py` | Specialized worker agents (Research, Finance, Analysis) |
| `memory_layer.py` | 4-tier memory (Working, Session, Semantic, Relational) |
| `consensus_engine.py` | DCBFT Byzantine Fault Tolerant voting |
| `llm_client.py` | Unified LLM client (GitHub Models, OpenAI, Azure) |

## 🔧 Configuration

### Environment Variables

```env
# LLM Provider (choose one)
GITHUB_TOKEN=ghp_your_token   # Recommended: Free with GitHub account
OPENAI_API_KEY=sk-your-key    # Alternative: OpenAI
LLM_PROVIDER=github           # Options: github, openai, azure

# Production Memory Backends (optional)
REDIS_URL=redis://localhost:6379/0
MILVUS_HOST=localhost
NEO4J_URI=bolt://localhost:7687
```

### LLM Providers

| Provider | Token Variable | Best For |
| -------- | -------------- | -------- |
| **GitHub Models** | `GITHUB_TOKEN` | Free, recommended |
| **OpenAI** | `OPENAI_API_KEY` | Production quality |
| **Azure OpenAI** | `AZURE_OPENAI_API_KEY` | Enterprise |

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=. --cov-report=html

# Run integration test
python main.py orchestrate "Test objective for CI"
```

## 🐳 Docker

### Build

```bash
docker build -t collectivebrain .
```

### Run

```bash
# Interactive orchestration
docker run -it --rm collectivebrain orchestrate "Build an API"

# Status check
docker run -it --rm collectivebrain status
```

### Docker Compose Profiles

| Profile       | Services                          | Use Case              |
| ------------- | --------------------------------- | --------------------- |
| (default)     | brain                             | Local development     |
| `production`  | brain, redis, milvus, etcd, minio | Production deployment |

## 🔐 DCBFT Consensus Protocol

The consensus engine implements the Byzantine Fault Tolerance formula:

```text
N >= 3f + 1
```

Where:

- **N** = Total number of agents
- **f** = Maximum faulty/Byzantine agents tolerated
- **Quorum** = ~66% (super-majority required)

### Example

```python
from consensus_engine import DCBFTEngine, VoteType

# Allow for 1 faulty agent (requires 4 total)
engine = DCBFTEngine(max_faulty_agents=1)

# Initiate vote
session = engine.initiate_vote(
    "deploy-001",
    "Deploy to production",
    ["gemini", "claude", "codex", "grok"]
)

# Cast votes
engine.cast_vote("deploy-001", "gemini", VoteType.APPROVE, "Tested OK")
engine.cast_vote("deploy-001", "claude", VoteType.APPROVE, "Approved")
engine.cast_vote("deploy-001", "codex", VoteType.APPROVE, "Ready")
engine.cast_vote("deploy-001", "grok", VoteType.REJECT, "Needs review")

# Tally
result = engine.tally_votes("deploy-001")
print(f"Result: {result['decision']}")  # consensus_reached
```

## 📁 Project Structure

```text
CollectiveBrain_V1/
├── main.py              # CLI entry point
├── orchestrator.py      # Objective decomposition
├── worker_pool.py       # Worker agent pool
├── memory_layer.py      # Unified memory system
├── consensus_engine.py  # DCBFT consensus
├── llm_client.py        # LLM integration
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container build
├── docker-compose.yml   # Full stack deployment
├── .env.example         # Environment template
├── tests/               # Test suite
│   └── test_brain.py
└── .github/
    └── workflows/
        └── ci.yml       # CI/CD pipeline
```

## 🛤️ Roadmap

- [x] Core orchestrator with LLM decomposition
- [x] Worker pool with specialized agents
- [x] DCBFT consensus engine
- [x] 4-tier memory layer (stubs)
- [x] Docker containerization
- [x] CI/CD pipeline
- [x] REST API interface (`api.py`)
- [ ] Redis integration for SessionMemory
- [ ] Milvus integration for SemanticMemory
- [ ] Neo4j integration for RelationalMemory
- [ ] Web dashboard

## 🌐 REST API

Start the API server:

```bash
# Using uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000

# Or run the script
python api.py
```

### Endpoints

| Method | Endpoint                 | Description                   |
| ------ | ------------------------ | ----------------------------- |
| GET    | `/health`                | Health check                  |
| GET    | `/status`                | System status                 |
| POST   | `/orchestrate`           | Decompose & execute objective |
| POST   | `/consensus/initiate`    | Start a DCBFT vote            |
| POST   | `/consensus/{id}/vote`   | Cast a vote                   |
| POST   | `/consensus/{id}/tally`  | Tally and get result          |
| POST   | `/memory/working`        | Add to working memory         |
| GET    | `/memory/status`         | Memory layer status           |
| GET    | `/workers`               | List worker pool              |

### API Example

```bash
# Orchestrate an objective
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"objective": "Build a RAG pipeline"}'

# Initiate consensus
curl -X POST http://localhost:8000/consensus/initiate \
  -H "Content-Type: application/json" \
  -d '{"description": "Deploy to production"}'
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

*Built for the gAIng Collective* 🧠
