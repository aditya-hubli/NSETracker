# 🚀 Real-Time Event-Driven Data Platform

[![CI](https://github.com/aditya-hubli/Real-Time-Event-Driven-Data-Platform/actions/workflows/ci.yml/badge.svg)](https://github.com/aditya-hubli/Real-Time-Event-Driven-Data-Platform/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready, event-driven data platform built with FastAPI, Redpanda (Kafka-compatible), Supabase (PostgreSQL), and Next.js.

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  user-service   │     │  order-service  │     │ payment-service │
│    (FastAPI)    │     │    (FastAPI)    │     │    (FastAPI)    │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌────────────────────────┐
                    │       Redpanda         │
                    │   (Kafka-compatible)   │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │   stream-processor     │
                    │  - Aggregations        │
                    │  - Deduplication       │
                    └───────────┬────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              ▼                                   ▼
    ┌──────────────────┐              ┌──────────────────┐
    │   Supabase       │              │  Parquet Files   │
    │   (PostgreSQL)   │              │  (Raw Events)    │
    └────────┬─────────┘              └──────────────────┘
             │
             ▼
    ┌──────────────────┐
    │   analytics-api  │
    │    (FastAPI)     │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │    Dashboard     │
    │    (Next.js)     │
    └──────────────────┘
```

## 📦 Tech Stack

| Component | Technology |
|-----------|------------|
| **Event Producers** | FastAPI (Python) |
| **Message Broker** | Redpanda (Kafka-compatible) |
| **Stream Processing** | Python + aiokafka |
| **Database** | Supabase (PostgreSQL) |
| **Analytics API** | FastAPI (Python) |
| **Dashboard** | Next.js (TypeScript) |
| **Deployment** | Railway |
| **CI/CD** | GitHub Actions |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Node.js 20+ (for dashboard)
- Make (optional)

### 1. Clone the repository

```bash
git clone https://github.com/aditya-hubli/Real-Time-Event-Driven-Data-Platform.git
cd Real-Time-Event-Driven-Data-Platform
```

### 2. Set up environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# - Supabase URL and keys
# - Other configuration
```

### 3. Install dependencies

```bash
# Using make
make install-dev

# Or manually
pip install -e ".[dev,test]"
pre-commit install
```

### 4. Start infrastructure

```bash
# Start Redpanda
make docker-up

# Or manually
docker-compose -f infra/docker-compose.yml up -d
```

### 5. Apply database schema

1. Go to [Supabase SQL Editor](https://app.supabase.com)
2. Copy contents of `infra/supabase/schema.sql`
3. Run the query

### 6. Run services

```bash
# Terminal 1: User Service
make run-user-service

# Terminal 2: Order Service
make run-order-service

# Terminal 3: Payment Service
make run-payment-service

# Terminal 4: Stream Processor
make run-stream-processor

# Terminal 5: Analytics API
make run-analytics-api

# Terminal 6: Dashboard
make run-dashboard
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run only unit tests
make test-unit
```

## 📁 Project Structure

```
event-driven-data-platform/
├── .github/
│   ├── workflows/
│   │   └── ci.yml              # CI/CD pipeline
│   ├── CODEOWNERS              # Code ownership
│   └── pull_request_template.md
│
├── services/
│   ├── user-service/           # User event producer
│   ├── order-service/          # Order event producer
│   ├── payment-service/        # Payment event producer
│   ├── stream-processor/       # Event consumer & aggregator
│   ├── analytics-api/          # REST API for analytics
│   └── dashboard/              # Next.js dashboard
│
├── shared/
│   └── python/                 # Shared Python modules
│       ├── config.py
│       ├── logging_config.py
│       ├── schemas.py
│       └── kafka_client.py
│
├── infra/
│   ├── docker-compose.yml      # Local development
│   └── supabase/
│       ├── schema.sql          # Database schema
│       └── seed.sql            # Test data
│
├── .env.example                # Environment template
├── pyproject.toml              # Python project config
├── Makefile                    # Development commands
└── README.md
```

## 🔄 Development Workflow

1. Create feature branch from `develop`
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/my-feature
   ```

2. Make changes and commit
   ```bash
   git add .
   git commit -m "feat: add my feature"
   ```

3. Push and create PR
   ```bash
   git push -u origin feature/my-feature
   # Create PR: feature/my-feature → develop
   ```

4. After CI passes, merge to `develop`

5. Release to production
   ```bash
   git checkout main
   git merge develop
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin main --tags
   ```

## 📊 API Documentation

Once services are running:

- **User Service**: http://localhost:8001/docs
- **Order Service**: http://localhost:8002/docs
- **Payment Service**: http://localhost:8003/docs
- **Analytics API**: http://localhost:8000/docs

## 🔐 Environment Variables

See `.env.example` for all required variables:

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase anonymous key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key |
| `KAFKA_BOOTSTRAP_SERVERS` | Redpanda/Kafka broker address |

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

Built with ❤️ by [Aditya Hubli](https://github.com/aditya-hubli)
