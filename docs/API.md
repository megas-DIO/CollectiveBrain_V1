# CollectiveBrain API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production, implement:
- API keys
- OAuth 2.0
- JWT tokens

## Endpoints

### Health Check

#### `GET /health`

Check system health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-13T10:30:00.000000",
  "version": "1.0.0"
}
```

---

### System Status

#### `GET /status`

Get comprehensive system status.

**Response:**
```json
{
  "orchestrator": {
    "active_tasks": 2,
    "completed_tasks": 15
  },
  "worker_pool": {
    "total_workers": 4,
    "available_workers": 3,
    "workers": [...]
  },
  "memory": {
    "working_memory": {
      "size": 45,
      "budget": 50,
      "is_full": false
    },
    "session_memory": {
      "active_sessions": 2
    },
    "semantic_memory": {
      "indexed_documents": 128
    },
    "relational_memory": {
      "nodes": 256,
      "relationships": 512
    }
  },
  "consensus_engine": {
    "min_required_agents": 4,
    "pending_decisions": 1,
    "finalized_decisions": 8
  },
  "supervisor": {
    "synthesis_count": 15
  },
  "execution_history": 15
}
```

---

### Process Objective

#### `POST /objectives`

Process a high-level objective through the CollectiveBrain system.

**Request Body:**
```json
{
  "objective": "Build vector search capability for semantic document retrieval",
  "require_consensus": true
}
```

**Parameters:**
- `objective` (string, required): The high-level objective to process
- `require_consensus` (boolean, optional): Whether to require consensus (default: true)

**Response:**
```json
{
  "execution_id": "exec_20260113_103000",
  "task_id": "uuid-1234-5678",
  "status": "completed_with_consensus",
  "objective": "Build vector search capability for semantic document retrieval",
  "timestamp": "2026-01-13T10:30:00.000000"
}
```

**Status Values:**
- `completed_with_consensus`: Successfully completed with consensus approval
- `completed_without_consensus`: Completed without requiring consensus
- `quality_failed`: Quality validation failed
- `consensus_failed`: Consensus was not reached
- `error`: Processing error occurred

---

### Get Objective Result

#### `GET /objectives/{execution_id}`

Get the full result of a processed objective.

**Path Parameters:**
- `execution_id` (string): The execution ID returned from POST /objectives

**Response:**
```json
{
  "execution_id": "exec_20260113_103000",
  "task_id": "uuid-1234-5678",
  "status": "completed_with_consensus",
  "objective": "Build vector search capability",
  "sub_goals": [
    "Research requirements for: Build vector search capability",
    "Design architecture for: Build vector search capability",
    "Create implementation plan for: Build vector search capability"
  ],
  "worker_results": [
    {
      "task_id": "uuid-1234-5678",
      "agent_id": "agent-uuid-1",
      "role": "Research",
      "result": "Found 3 vector database options...",
      "reflection_token": "[IsRel]",
      "status": "completed"
    }
  ],
  "synthesis": {
    "task_id": "uuid-1234-5678",
    "total_workers": 3,
    "worker_roles": ["Research", "Analysis", "Implementation"],
    "combined_output": "...",
    "status": "synthesized"
  },
  "validation": {
    "task_id": "uuid-1234-5678",
    "passed": true,
    "checks": {...}
  },
  "consensus": {
    "decision_id": "finalize_uuid-1234-5678",
    "decision": "consensus_reached",
    "vote_breakdown": {
      "approve": 3,
      "reject": 0,
      "abstain": 1,
      "total": 4
    },
    "consensus_percentage": 75.0
  },
  "timestamp": "2026-01-13T10:30:00.000000"
}
```

---

### Execution History

#### `GET /history?limit=10`

Get recent execution history.

**Query Parameters:**
- `limit` (integer, optional): Maximum number of executions to return (default: 10)

**Response:**
```json
{
  "total": 15,
  "limit": 10,
  "executions": [
    {
      "execution_id": "exec_20260113_103000",
      "task_id": "uuid-1234-5678",
      "objective": "...",
      "status": "completed_with_consensus",
      "timestamp": "2026-01-13T10:30:00.000000"
    }
  ]
}
```

---

### Cast Vote

#### `POST /consensus/vote`

Cast a vote for a consensus decision.

**Request Body:**
```json
{
  "decision_id": "finalize_uuid-1234-5678",
  "agent_id": "agent-uuid-1",
  "vote": "approve",
  "justification": "Quality validation passed successfully"
}
```

**Parameters:**
- `decision_id` (string, required): The decision ID to vote on
- `agent_id` (string, required): The voting agent's ID
- `vote` (string, required): Vote type ("approve", "reject", "abstain")
- `justification` (string, optional): Reasoning for the vote

**Response:**
```json
{
  "decision_id": "finalize_uuid-1234-5678",
  "agent_id": "agent-uuid-1",
  "vote_recorded": "approve",
  "total_votes": 3,
  "quorum_required": 3,
  "status": "recorded"
}
```

---

### Get Decision Status

#### `GET /consensus/{decision_id}`

Get the current status of a consensus decision.

**Path Parameters:**
- `decision_id` (string): The decision ID

**Response:**
```json
{
  "decision_id": "finalize_uuid-1234-5678",
  "description": "Finalize synthesis for task uuid-1234-5678",
  "required_agents": ["agent-1", "agent-2", "agent-3", "agent-4"],
  "votes": {
    "agent-1": {
      "vote": "approve",
      "justification": "Quality validation passed",
      "timestamp": "2026-01-13T10:30:00.000000"
    }
  },
  "quorum_required": 3,
  "status": "pending",
  "is_finalized": false
}
```

---

### Tally Votes

#### `POST /consensus/{decision_id}/tally`

Tally votes for a consensus decision.

**Path Parameters:**
- `decision_id` (string): The decision ID to tally

**Response:**
```json
{
  "decision_id": "finalize_uuid-1234-5678",
  "decision": "consensus_reached",
  "vote_breakdown": {
    "approve": 3,
    "reject": 0,
    "abstain": 1,
    "total": 4
  },
  "quorum_required": 3,
  "quorum_met": true,
  "consensus_percentage": 75.0,
  "finalized_at": "2026-01-13T10:30:05.000000"
}
```

---

### Worker Pool Status

#### `GET /workers`

Get status of all worker agents.

**Response:**
```json
{
  "total_workers": 4,
  "available_workers": 3,
  "workers": [
    {
      "agent_id": "agent-uuid-1",
      "role": "Research",
      "current_task": null,
      "tasks_completed": 15,
      "is_available": true
    }
  ]
}
```

---

### Memory Status

#### `GET /memory`

Get status of memory layers.

**Response:**
```json
{
  "working_memory": {
    "size": 45,
    "budget": 50,
    "is_full": false
  },
  "session_memory": {
    "active_sessions": 2
  },
  "semantic_memory": {
    "indexed_documents": 128
  },
  "relational_memory": {
    "nodes": 256,
    "relationships": 512
  }
}
```

---

### Configuration

#### `GET /config`

Get current system configuration (non-sensitive values only).

**Response:**
```json
{
  "environment": "production",
  "working_memory_budget": 50,
  "max_faulty_agents": 1,
  "min_required_agents": 4,
  "quality_criteria": {
    "min_workers": 3,
    "require_consensus": true
  }
}
```

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently not implemented. For production, consider:
- Request rate limiting per IP/API key
- Concurrent request limits
- Quota management

## Examples

### cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# Process objective
curl -X POST http://localhost:8000/objectives \
  -H "Content-Type: application/json" \
  -d '{
    "objective": "Build recommendation system",
    "require_consensus": true
  }'

# Get execution result
curl http://localhost:8000/objectives/exec_20260113_103000

# Get system status
curl http://localhost:8000/status

# Cast vote
curl -X POST http://localhost:8000/consensus/vote \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": "finalize_uuid-1234",
    "agent_id": "agent-1",
    "vote": "approve",
    "justification": "Looks good"
  }'
```

### Python Examples

```python
import requests

# Process objective
response = requests.post(
    "http://localhost:8000/objectives",
    json={
        "objective": "Build recommendation system",
        "require_consensus": True
    }
)
result = response.json()
print(f"Execution ID: {result['execution_id']}")

# Get full result
execution_id = result['execution_id']
response = requests.get(f"http://localhost:8000/objectives/{execution_id}")
full_result = response.json()
print(f"Status: {full_result['status']}")
```
