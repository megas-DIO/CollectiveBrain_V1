# CollectiveBrain Deployment Guide

## Quick Start

### Prerequisites

- Docker and Docker Compose (for containerized deployment)
- Python 3.11+ (for local development)
- Git

### Local Development Setup

1. **Clone the repository:**
```bash
git clone https://github.com/your-org/CollectiveBrain_V1.git
cd CollectiveBrain_V1
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run standalone application:**
```bash
python collective_brain.py
```

5. **Run API server:**
```bash
python api.py
# Or with uvicorn directly:
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

#### Option 1: Standalone Container (No External Services)

```bash
# Build image
docker build -t collective-brain:latest .

# Run container
docker run -p 8000:8000 collective-brain:latest
```

This runs the API in standalone mode with in-memory backends (no Redis, Milvus, Neo4j).

#### Option 2: Full Stack with Docker Compose (Recommended)

1. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
nano .env
```

2. **Start all services:**
```bash
docker-compose up -d
```

This starts:
- CollectiveBrain API (port 8000)
- Redis (port 6379)
- Milvus (port 19530)
- Neo4j (ports 7474, 7687)
- Supporting services (etcd, MinIO)

3. **Check service health:**
```bash
docker-compose ps
```

4. **View logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f collective-brain
```

5. **Stop services:**
```bash
docker-compose down
```

6. **Remove all data (destructive):**
```bash
docker-compose down -v
```

### Production Deployment

#### AWS Deployment

**Architecture:**
```
Internet -> ALB -> ECS Fargate (CollectiveBrain)
                    |
                    +-> ElastiCache (Redis)
                    +-> Milvus (EC2/EKS)
                    +-> Neo4j AuraDB
```

**Steps:**

1. **Set up ElastiCache (Redis):**
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id cbrain-session-cache \
  --engine redis \
  --cache-node-type cache.t3.medium \
  --num-cache-nodes 1
```

2. **Deploy Milvus on EC2 or EKS:**
```bash
# Using Helm on EKS
helm repo add milvus https://milvus-io.github.io/milvus-helm/
helm install cbrain-milvus milvus/milvus
```

3. **Set up Neo4j AuraDB:**
- Visit https://neo4j.com/cloud/aura/
- Create a new instance
- Note connection URI and credentials

4. **Deploy to ECS Fargate:**
```bash
# Build and push image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t collective-brain .
docker tag collective-brain:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/collective-brain:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/collective-brain:latest

# Create ECS task definition and service
aws ecs create-service \
  --cluster cbrain-cluster \
  --service-name collective-brain \
  --task-definition cbrain-task:1 \
  --desired-count 2 \
  --load-balancers targetGroupArn=<target-group-arn>,containerName=collective-brain,containerPort=8000
```

#### Kubernetes Deployment

1. **Create ConfigMap:**
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cbrain-config
data:
  CB_ENVIRONMENT: "production"
  CB_LOG_LEVEL: "INFO"
  CB_API_HOST: "0.0.0.0"
  CB_API_PORT: "8000"
```

2. **Create Secret:**
```bash
kubectl create secret generic cbrain-secrets \
  --from-literal=neo4j-password=<password> \
  --from-literal=redis-password=<password>
```

3. **Deploy application:**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: collective-brain
spec:
  replicas: 3
  selector:
    matchLabels:
      app: collective-brain
  template:
    metadata:
      labels:
        app: collective-brain
    spec:
      containers:
      - name: collective-brain
        image: collective-brain:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: cbrain-config
        env:
        - name: CB_MEMORY_NEO4J_PASSWORD
          valueFrom:
            secretKeyRef:
              name: cbrain-secrets
              key: neo4j-password
```

4. **Create Service:**
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: collective-brain
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: collective-brain
```

5. **Apply configurations:**
```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Environment Configuration

#### Required Environment Variables

```bash
# General
CB_ENVIRONMENT=production
CB_LOG_LEVEL=INFO

# Memory Layer
CB_MEMORY_REDIS_HOST=redis.example.com
CB_MEMORY_REDIS_PORT=6379
CB_MEMORY_REDIS_PASSWORD=<secure-password>

CB_MEMORY_MILVUS_HOST=milvus.example.com
CB_MEMORY_MILVUS_PORT=19530

CB_MEMORY_NEO4J_URI=bolt://neo4j.example.com:7687
CB_MEMORY_NEO4J_USER=neo4j
CB_MEMORY_NEO4J_PASSWORD=<secure-password>

# API
CB_API_HOST=0.0.0.0
CB_API_PORT=8000
CB_API_WORKERS=4

# Consensus
CB_CONSENSUS_MAX_FAULTY_AGENTS=1

# Quality
CB_QUALITY_MIN_WORKERS=3
CB_QUALITY_REQUIRE_CONSENSUS=true
```

### Monitoring and Observability

#### Logging

Logs are output in JSON format for easy parsing:

```json
{
  "timestamp": "2026-01-13T10:30:00.000000",
  "level": "INFO",
  "logger": "collective_brain",
  "message": "Processing objective",
  "module": "collective_brain",
  "function": "process_objective"
}
```

**Integration with logging platforms:**

- **Elasticsearch/Kibana**: Use Filebeat to ship logs
- **Datadog**: Use Datadog agent
- **CloudWatch**: Use awslogs Docker logging driver

#### Metrics

System exposes metrics for monitoring:

```python
from logger import get_metrics

metrics = get_metrics()
print(metrics.get_all())
```

**Key metrics:**
- `objectives_processed`: Total objectives processed
- `consensus_decisions`: Total consensus decisions
- `worker_tasks_completed`: Total worker tasks
- `errors`: Total errors encountered

#### Health Checks

```bash
# Basic health
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/status
```

### Backup and Recovery

#### Neo4j Backup

```bash
# Export database
docker exec collective-brain-neo4j neo4j-admin database dump neo4j --to-path=/backups

# Restore
docker exec collective-brain-neo4j neo4j-admin database load neo4j --from-path=/backups/neo4j.dump
```

#### Milvus Backup

```bash
# Backup Milvus data directory
docker exec collective-brain-milvus tar czf /backup/milvus-backup.tar.gz /var/lib/milvus

# Restore
docker exec collective-brain-milvus tar xzf /backup/milvus-backup.tar.gz -C /
```

### Scaling

#### Horizontal Scaling

Multiple API instances can run concurrently:

```bash
# Docker Compose
docker-compose up -d --scale collective-brain=3

# Kubernetes
kubectl scale deployment collective-brain --replicas=5
```

**Considerations:**
- Shared Redis for session coordination
- Shared Neo4j and Milvus for memory
- Stateless API design enables easy scaling

#### Vertical Scaling

Adjust resource limits:

```yaml
# Docker Compose
services:
  collective-brain:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Security Best Practices

1. **Network Isolation:**
   - Use private networks for internal services
   - Expose only API endpoint publicly

2. **Authentication:**
   - Implement API key authentication
   - Use OAuth 2.0 for user authentication

3. **Encryption:**
   - TLS/SSL for all external connections
   - Encrypt data at rest in databases

4. **Secrets Management:**
   - Use AWS Secrets Manager, HashiCorp Vault, or K8s Secrets
   - Never commit credentials to version control

5. **Rate Limiting:**
   - Implement rate limiting at API gateway level
   - Protect against DoS attacks

### Troubleshooting

#### Common Issues

**Issue: API won't start**
```bash
# Check logs
docker-compose logs collective-brain

# Common causes:
# - Port 8000 already in use
# - Missing environment variables
# - Database connection failures
```

**Issue: Worker tasks hanging**
```bash
# Check worker pool status
curl http://localhost:8000/workers

# Restart service
docker-compose restart collective-brain
```

**Issue: Memory layer errors**
```bash
# Check Redis
redis-cli ping

# Check Milvus
curl http://localhost:9091/healthz

# Check Neo4j
cypher-shell -u neo4j -p password "RETURN 1"
```

### Performance Tuning

#### Memory Layer

```bash
# Redis
CB_MEMORY_WORKING_MEMORY_BUDGET=100  # Increase if needed

# Milvus
# Tune HNSW parameters for better performance
# - M: number of connections per layer
# - efConstruction: search quality during construction
```

#### API Workers

```bash
# Increase API workers for better concurrency
CB_API_WORKERS=8
```

#### Database Connections

```bash
# Neo4j
NEO4J_dbms_memory_pagecache_size=2G
NEO4J_dbms_memory_heap_max__size=2G
```

### Upgrade Strategy

1. **Backup all data**
2. **Test in staging environment**
3. **Use blue-green deployment:**
   - Deploy new version alongside old
   - Gradually shift traffic
   - Rollback if issues detected

```bash
# Blue-green with Docker
docker-compose -f docker-compose.yml -f docker-compose.green.yml up -d
# Verify green deployment
docker-compose -f docker-compose.yml down
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-org/CollectiveBrain_V1/issues
- Documentation: https://github.com/your-org/CollectiveBrain_V1/docs
