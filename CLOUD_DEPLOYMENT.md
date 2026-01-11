# Cloud Deployment Guide

This guide explains how to deploy the Real-Time Event-Driven Data Platform to various cloud providers.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Load Balancer / CDN                         │
│                    (AWS ALB / GCP LB / Azure LB)                    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
        ┌───────────────────┐           ┌───────────────────┐
        │  Next.js Frontend │           │    API Gateway    │
        │   (Vercel/Cloud)  │           │   (Port 8000)     │
        └───────────────────┘           └───────────────────┘
                                                 │
                    ┌─────────────┬──────────────┼──────────────┬─────────────┐
                    │             │              │              │             │
                    ▼             ▼              ▼              ▼             ▼
            ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
            │   User    │ │ Analytics │ │ Sentiment │ │   Stock   │ │  Notif.   │
            │  Service  │ │  Service  │ │  Service  │ │  Service  │ │  Service  │
            │  (8001)   │ │  (8002)   │ │  (8003)   │ │  (8004)   │ │  (8005)   │
            └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘
                    │             │              │              │
                    │         ┌───┴──────────────┴───┐         │
                    │         │    ML Model Store    │         │
                    │         │  (S3/GCS/Blob)       │         │
                    │         └──────────────────────┘         │
                    │                                          │
                    └──────────────────┬───────────────────────┘
                                       │
                              ┌────────┴────────┐
                              │    Supabase     │
                              │   (PostgreSQL)  │
                              └─────────────────┘
```

## Prerequisites

- Docker and Docker Compose installed
- Cloud CLI tools (AWS CLI, gcloud, or az)
- Access to container registry (ECR, GCR, ACR)
- Supabase project configured

## Local Development

```bash
# Start all services locally
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## AWS Deployment

### Option 1: AWS ECS with Fargate

1. **Push images to ECR:**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

# Create repositories
aws ecr create-repository --repository-name stock-platform/api-gateway
aws ecr create-repository --repository-name stock-platform/analytics-service
aws ecr create-repository --repository-name stock-platform/sentiment-service
# ... for each service

# Build and push
docker build -f services/api_gateway/Dockerfile -t stock-platform/api-gateway .
docker tag stock-platform/api-gateway:latest <account>.dkr.ecr.us-east-1.amazonaws.com/stock-platform/api-gateway:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/stock-platform/api-gateway:latest
```

2. **Create ECS Task Definitions** (see `infra/aws/task-definitions/`)

3. **Deploy with CDK or Terraform:**
```bash
cd infra/aws
terraform init
terraform apply
```

### Option 2: AWS App Runner (Simpler)

For each service:
```bash
aws apprunner create-service \
  --service-name analytics-service \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "<account>.dkr.ecr.us-east-1.amazonaws.com/stock-platform/analytics-service:latest",
      "ImageRepositoryType": "ECR"
    }
  }'
```

### ML Models on AWS

Store models in S3 and mount using s3fs:
```yaml
# In ECS task definition
volumes:
  - name: ml-models
    efsVolumeConfiguration:
      fileSystemId: fs-xxxxx
      rootDirectory: /models
```

---

## Google Cloud Deployment

### Option 1: Cloud Run (Recommended)

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/analytics-service services/analytics_service/

# Deploy to Cloud Run
gcloud run deploy analytics-service \
  --image gcr.io/PROJECT_ID/analytics-service \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "ENABLE_ML_PREDICTIONS=true" \
  --set-secrets "SUPABASE_URL=supabase-url:latest"
```

### Option 2: GKE (Kubernetes)

```bash
# Create cluster
gcloud container clusters create stock-platform --num-nodes=3

# Apply Kubernetes manifests
kubectl apply -f infra/k8s/
```

### ML Models on GCP

```bash
# Upload models to GCS
gsutil cp -r models/ gs://your-bucket/ml-models/

# Mount in Cloud Run (using gcsfuse)
gcloud run deploy sentiment-service \
  --add-cloudsql-instances=... \
  --set-env-vars "ML_MODEL_PATH=/models" \
  --execution-environment gen2 \
  --add-volume name=ml-models,type=cloud-storage,bucket=your-bucket \
  --add-volume-mount volume=ml-models,mount-path=/models
```

---

## Azure Deployment

### Option 1: Azure Container Apps

```bash
# Create Container App Environment
az containerapp env create \
  --name stock-platform-env \
  --resource-group stock-platform-rg \
  --location eastus

# Deploy service
az containerapp create \
  --name analytics-service \
  --resource-group stock-platform-rg \
  --environment stock-platform-env \
  --image stockplatform.azurecr.io/analytics-service:latest \
  --target-port 8002 \
  --ingress external
```

### ML Models on Azure

Use Azure Blob Storage with blobfuse:
```bash
# Create storage container
az storage container create --name ml-models

# Upload models
az storage blob upload-batch -d ml-models -s ./models/
```

---

## ML Model Deployment

### Deploying FinBERT for Sentiment Analysis

1. **Download and prepare model:**
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")

model.save_pretrained("./models/finbert")
tokenizer.save_pretrained("./models/finbert")
```

2. **Upload to cloud storage:**
```bash
# AWS
aws s3 sync ./models/ s3://your-bucket/models/

# GCP
gsutil -m cp -r ./models/ gs://your-bucket/models/

# Azure
az storage blob upload-batch -d models -s ./models/
```

3. **Enable ML in services:**
```bash
# Update environment variables
ENABLE_ML_SENTIMENT=true
ML_MODEL_PATH=/app/models
```

### Deploying Custom LSTM Model

1. Train your model locally:
```python
# See services/analytics_service/train_model.py (coming soon)
```

2. Export as TorchScript or ONNX:
```python
torch.jit.save(torch.jit.script(model), "models/lstm_predictor.pt")
```

3. Upload and configure as above.

---

## Environment Variables for Production

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | Yes |
| `JWT_SECRET_KEY` | Secret for JWT signing | Yes |
| `ENABLE_ML_PREDICTIONS` | Enable ML-based predictions | No |
| `ENABLE_ML_SENTIMENT` | Enable ML-based sentiment | No |
| `ML_MODEL_PATH` | Path to ML models | No |
| `NEWS_API_KEY` | NewsAPI key for news | No |

---

## Scaling Recommendations

### Horizontal Scaling

- **Analytics Service**: CPU-intensive, scale based on CPU (target 70%)
- **Sentiment Service**: Memory-intensive (ML models), scale based on memory
- **Stock Service**: I/O-bound, scale based on request count
- **User Service**: Low resource, single instance usually sufficient

### Caching Strategy

- Use Supabase edge functions for caching
- Implement Redis cluster for high-traffic deployments
- CDN for static assets (Next.js handled by Vercel)

### Cost Optimization

1. **Use spot/preemptible instances** for non-critical batch processing
2. **Schedule scaling** during market hours (9:15 AM - 3:30 PM IST)
3. **Use reserved instances** for baseline capacity

---

## Monitoring & Observability

### Recommended Stack

- **Metrics**: Prometheus + Grafana
- **Logs**: Loki or CloudWatch/Stackdriver
- **Traces**: Jaeger or Cloud Trace
- **Alerts**: PagerDuty or Opsgenie

### Key Metrics to Monitor

1. API response times (P50, P95, P99)
2. ML inference latency
3. Cache hit rates
4. Error rates by service
5. Stock data freshness

---

## Security Checklist

- [ ] Enable HTTPS everywhere
- [ ] Use secrets manager for credentials
- [ ] Enable VPC/private networking
- [ ] Set up WAF rules
- [ ] Configure rate limiting
- [ ] Enable audit logging
- [ ] Regular security scans
