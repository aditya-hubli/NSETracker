# Real-Time Stock Data Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A professional real-time stock data platform built with FastAPI, Next.js, and Supabase. Features user and admin dashboards with authentication.

## Overview

This platform provides real-time stock market data visualization with role-based access control:

- **User Dashboard**: Search stocks, view real-time prices, manage watchlists
- **Admin Dashboard**: User management, platform analytics, system settings
- **Real-Time Data**: Live stock quotes powered by Yahoo Finance API
- **Modern Stack**: FastAPI backend, Next.js frontend, JWT authentication

## Features

### User Features
- Real-time stock quotes and price tracking
- Stock search with instant results
- Personal watchlists (create, manage, delete)
- Price history charts and market data
- User settings and preferences

### Sentiment Analysis (NEW)
- News sentiment from multiple sources
- Reddit/social media sentiment tracking
- Trending stocks based on mentions
- Sentiment classification (bullish/bearish)
- Real-time sentiment updates

### Technical Analytics (NEW)
- Technical indicators (SMA, EMA, MACD, RSI, Bollinger Bands)
- Trading signals (Strong Buy to Strong Sell)
- Volume analysis and unusual activity detection
- Volatility metrics and ATR
- Support/Resistance level detection
- Stock screener with multiple criteria
- Market heatmap visualization

### Alerts & Notifications (NEW)
- Price alerts (above/below/percent change)
- Real-time WebSocket notifications
- News alerts and sentiment shifts
- Volume spike detection
- Push notifications

### Admin Features
- Platform overview dashboard with key metrics
- User management (view, create, manage users)
- Platform analytics and usage statistics
- System settings configuration
- API monitoring

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend | FastAPI (Python 3.11+) | REST APIs & authentication |
| Stock Data | yfinance | Real-time market data |
| Database | Supabase (PostgreSQL) | User and data storage |
| Frontend | Next.js 14 (TypeScript) | Modern React dashboard |
| Styling | Tailwind CSS | Dark theme UI |
| Auth | JWT tokens | Session management |
| Caching | In-memory (cachetools) | Request caching |
| Messaging | Kafka/Redpanda | Event streaming & pub/sub |
| Sentiment | VADER, TextBlob | NLP sentiment analysis |
| Technical | TA-Lib, Pandas | Technical indicators |
| Real-time | WebSockets | Live updates |

## Project Structure

```
project/
├── services/                 # Backend microservices
│   ├── api_gateway.py        # Unified API entry point
│   ├── user_service/         # Authentication & user management
│   ├── stock_service/        # Real-time stock data (Yahoo Finance)
│   ├── sentiment_service/    # News & social sentiment analysis (NEW)
│   ├── analytics_service/    # Technical indicators & screening (NEW)
│   ├── notification_service/ # Alerts & WebSocket updates (NEW)
│   ├── order_service/        # Order management
│   └── payment_service/      # Payment processing
├── shared/                   # Shared Python modules
│   ├── config.py             # Configuration
│   ├── schemas.py            # Pydantic models
│   ├── exceptions.py         # Custom exceptions
│   ├── cache.py              # In-memory caching
│   └── events.py             # Redpanda event streaming
├── dashboard/                # Next.js frontend
│   └── src/
│       ├── app/              # App router pages
│       │   ├── dashboard/    # User dashboard
│       │   ├── admin/        # Admin dashboard
│       │   ├── login/        # Authentication
│       │   └── register/
│       ├── components/       # React components
│       │   ├── layout/       # Layout components
│       │   ├── stocks/       # Stock-related components
│       │   ├── sentiment/    # Sentiment displays (NEW)
│       │   ├── analytics/    # Technical analysis (NEW)
│       │   └── notifications/# Alerts & notifications (NEW)
│       ├── contexts/         # React contexts (Auth)
│       └── lib/              # API & auth utilities
└── infra/                    # Infrastructure
    └── supabase/             # Database schemas
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Supabase account (free tier works)

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Set environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Run API Gateway
python -m services.api_gateway
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd dashboard

# Install dependencies
npm install

# Set environment variable
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

The dashboard will be available at `http://localhost:3000`

### Demo Login

Use these credentials to test the platform:

| Role | Email | Password |
|------|-------|----------|
| User | user@example.com | password123 |
| Admin | admin@example.com | password123 |

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user

### Stock Data
- `GET /api/v1/stocks/quote/{symbol}` - Get stock quote
- `GET /api/v1/stocks/quotes?symbols=...` - Get multiple quotes
- `GET /api/v1/stocks/history/{symbol}` - Get price history
- `GET /api/v1/stocks/search?q=...` - Search stocks
- `GET /api/v1/stocks/market/summary` - Market summary
- `GET /api/v1/stocks/market/movers` - Top gainers/losers

### Sentiment Analysis (NEW)
- `GET /api/v1/sentiment/stock/{symbol}` - Get comprehensive sentiment
- `GET /api/v1/sentiment/trending` - Get trending stocks
- `GET /api/v1/sentiment/news/{symbol}` - Get news with sentiment
- `GET /api/v1/sentiment/social/{symbol}` - Get social media posts

### Technical Analytics (NEW)
- `GET /api/v1/analytics/indicators/{symbol}` - Get technical indicators
- `GET /api/v1/analytics/signal/{symbol}` - Get trading signal
- `GET /api/v1/analytics/volume/{symbol}` - Volume analysis
- `GET /api/v1/analytics/volatility/{symbol}` - Volatility metrics
- `GET /api/v1/analytics/analysis/{symbol}` - Full technical analysis
- `POST /api/v1/analytics/screener` - Stock screener
- `GET /api/v1/analytics/heatmap` - Market heatmap data

### Notifications & Alerts (NEW)
- `WS /api/v1/notifications/ws/{user_id}` - Real-time WebSocket
- `POST /api/v1/notifications/alerts` - Create price alert
- `GET /api/v1/notifications/alerts` - Get user alerts
- `DELETE /api/v1/notifications/alerts/{id}` - Cancel alert
- `GET /api/v1/notifications/` - Get notifications
- `POST /api/v1/notifications/{id}/read` - Mark as read
- `GET /api/v1/notifications/unread-count` - Unread count

### Users
- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}` - Get user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

## Development

### Running Tests

```bash
# Run all tests
make test
# Or: pytest -v

# Run with coverage
make test-cov
```

### Code Quality

```bash
make lint          # Run linter
make format        # Format code
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Aditya Hubli**
- GitHub: [@aditya-hubli](https://github.com/aditya-hubli)
