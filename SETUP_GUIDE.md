# Setup Guide - Real-Time Event-Driven Data Platform

This guide provides detailed instructions for setting up the development environment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Supabase Configuration](#supabase-configuration)
4. [Running Locally](#running-locally)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Backend services |
| Node.js | 20+ | Dashboard frontend |
| Docker | Latest | Containerization |
| Git | Latest | Version control |
| Make | Latest | Development commands |

### Verify Installation

```bash
python --version   # Should be 3.11+
node --version     # Should be 20+
docker --version   # Should be recent
git --version      # Any recent version
make --version     # Any version (optional)
```

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/aditya-hubli/Real-Time-Event-Driven-Data-Platform.git
cd Real-Time-Event-Driven-Data-Platform
```

### 2. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install in development mode
pip install -e .

# Or install development dependencies manually
pip install pytest pytest-asyncio pytest-cov pydantic pydantic-settings ruff pre-commit
```

### 4. Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit with your credentials
# See Supabase Configuration section below
```

## Supabase Configuration

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up/Login
3. Click "New Project"
4. Fill in project details:
   - Name: `event-platform` (or your choice)
   - Database Password: (save this!)
   - Region: Choose closest to you
5. Wait for project to be created

### 2. Get Credentials

1. Go to Project Settings → API
2. Copy the following:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon/public key**: `eyJ...`
   - **service_role key**: `eyJ...` (keep secret!)

3. Go to Project Settings → Database
4. Copy **Connection string** (URI format)

### 3. Update .env File

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# Application Settings
ENVIRONMENT=development
DEBUG=true
```

### 4. Initialize Database Schema

```bash
# Connect to Supabase SQL Editor and run:
# infra/supabase/schema.sql

# Or use psql
psql $DATABASE_URL -f infra/supabase/schema.sql
```

## Running Locally

### Development Mode

```bash
# Run all services (when implemented)
make docker-up

# Run specific service
cd services/user-service
uvicorn main:app --reload --port 8001
```

### Docker Compose (Coming Soon)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Testing

### Run All Tests

```bash
# Using make
make test

# Using pytest directly
pytest shared/tests/ -v
```

### Run with Coverage

```bash
# Using make
make test-cov

# Using pytest directly
pytest shared/tests/ --cov=shared --cov-report=term-missing
```

### Run Specific Tests

```bash
# Run single file
pytest shared/tests/test_schemas.py -v

# Run single test
pytest shared/tests/test_schemas.py::test_user_event_creation -v
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Make sure PYTHONPATH includes project root
export PYTHONPATH=.

# Or install in development mode
pip install -e .
```

#### 2. Environment Variables Not Loading

```bash
# Verify .env file exists
ls -la .env

# Check file contents (be careful with secrets)
cat .env | head -5
```

#### 3. Database Connection Failed

- Check `DATABASE_URL` in `.env`
- Verify Supabase project is active
- Check IP allowlist in Supabase settings

#### 4. Lint Errors

```bash
# Auto-fix with ruff
make format

# Or manually
ruff format .
ruff check . --fix
```

### Getting Help

1. Check existing [GitHub Issues](https://github.com/aditya-hubli/Real-Time-Event-Driven-Data-Platform/issues)
2. Review [README.md](README.md)
3. Open a new issue with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, Python version, etc.)
