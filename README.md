# Real-Time Event-Driven Data Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A scalable, real-time data platform built with FastAPI, Redpanda, Supabase, and Next.js.

## 🌟 Overview

This platform demonstrates modern event-driven architecture patterns for processing and analyzing real-time data streams. It features:

- **Event-Driven Architecture**: Loosely coupled services communicating via message broker
- **Real-Time Processing**: Stream processing with Redpanda (Kafka-compatible)
- **Modern Stack**: FastAPI, Next.js, PostgreSQL (Supabase)
- **Production Ready**: CI/CD, testing, monitoring, Docker containers

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   User      │    │   Order     │    │  Payment    │
│  Service    │───▶│  Service    │───▶│  Service    │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌──────────────────────────────────────────────────┐
│                   Redpanda                        │
│              (Message Broker)                     │
└──────────────────────────────────────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Stream    │    │  Analytics  │    │  Supabase   │
│  Processor  │───▶│    API      │◀───│ (PostgreSQL)│
└─────────────┘    └──────┬──────┘    └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │   Next.js   │
                   │  Dashboard  │
                   └─────────────┘
```

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend Services | FastAPI (Python 3.11+) | REST APIs & event producers |
| Message Broker | Redpanda | Kafka-compatible streaming |
| Database | Supabase (PostgreSQL) | Persistent storage |
| Frontend | Next.js (TypeScript) | Real-time dashboard |
| Infrastructure | Docker, Railway | Containerization & hosting |
| CI/CD | GitHub Actions | Automated testing & deployment |

## 📁 Project Structure

```
├── services/              # Microservices
│   ├── user-service/      # User management
│   ├── order-service/     # Order processing
│   ├── payment-service/   # Payment handling
│   ├── stream-processor/  # Event stream processing
│   └── analytics-api/     # Analytics & reporting
├── shared/                # Shared Python modules
│   ├── config.py          # Configuration management
│   ├── schemas.py         # Pydantic models
│   ├── exceptions.py      # Custom exceptions
│   └── logging_config.py  # Structured logging
├── dashboard/             # Next.js frontend
├── infra/                 # Infrastructure configs
│   └── supabase/          # Database schemas
├── .github/               # GitHub Actions workflows
└── docs/                  # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+ (for dashboard)
- Docker & Docker Compose
- Make (optional, for convenience commands)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/aditya-hubli/Real-Time-Event-Driven-Data-Platform.git
   cd Real-Time-Event-Driven-Data-Platform
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Install dependencies**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install Python dependencies
   pip install -e .
   ```

4. **Run tests**
   ```bash
   make test
   # Or: pytest shared/tests/ -v
   ```

5. **Start services** (coming soon)
   ```bash
   make docker-up
   ```

## 🧪 Development

### Available Commands

```bash
make help          # Show all available commands
make lint          # Run linter
make format        # Format code
make test          # Run tests
make test-cov      # Run tests with coverage
make clean         # Clean cache files
```

### Code Quality

This project uses:
- **ruff** for linting and formatting
- **pytest** for testing
- **pre-commit** hooks for automated checks

```bash
# Install pre-commit hooks
pre-commit install

# Run checks manually
pre-commit run --all-files
```

## 📖 Documentation

- [Setup Guide](SETUP_GUIDE.md) - Detailed setup instructions
- [API Documentation](docs/api.md) - API reference (coming soon)
- [Architecture](docs/architecture.md) - System design (coming soon)

## 🗺️ Roadmap

- [x] Project setup & CI/CD
- [ ] User Service
- [ ] Order Service
- [ ] Payment Service
- [ ] Redpanda integration
- [ ] Stream Processor
- [ ] Analytics API
- [ ] Next.js Dashboard
- [ ] Railway deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Aditya Hubli**
- GitHub: [@aditya-hubli](https://github.com/aditya-hubli)
