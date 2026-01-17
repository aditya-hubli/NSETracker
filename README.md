# NSE Stock Tracker - Real-Time Event-Driven Data Platform

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16+-000000?logo=next.js&logoColor=white)](https://nextjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Project Overview

The NSE Stock Tracker is a comprehensive, production-ready platform designed to provide real-time stock market data and analysis for the Indian National Stock Exchange (NSE) and Bombay Stock Exchange (BSE). This platform addresses the need for retail investors and traders to access professional-grade market analysis tools that are typically available only through expensive institutional platforms.

### The Problem

Individual investors in India face several challenges:
- Lack of access to real-time market data and analysis tools
- Difficulty in tracking multiple stocks across their portfolio
- Missing timely price alerts when stocks reach target levels
- Limited access to AI-powered sentiment analysis from financial news
- Complex technical analysis requiring specialized knowledge
- Inability to automate market monitoring and get instant notifications

### The Solution

This platform provides an enterprise-grade solution that democratizes access to sophisticated market analysis tools:

1. **Real-Time Data Access**: Leverages Yahoo Finance API to provide live quotes for over 1500 NSE and BSE listed stocks, including major indices like NIFTY 50, SENSEX, and Bank NIFTY.

2. **Event-Driven Architecture**: Built on Apache Kafka for reliable, scalable event streaming. This ensures that price updates, alerts, and notifications are processed asynchronously and can handle high throughput without blocking operations.

3. **AI-Powered Insights**: Integrates FinBERT (Financial BERT), a specialized natural language processing model trained on financial text, to analyze news sentiment and provide actionable insights about market sentiment for individual stocks.

4. **Intelligent Alerting**: Implements a sophisticated notification system that monitors price movements in real-time and sends beautifully formatted email alerts when user-defined conditions are met.

5. **Technical Analysis**: Provides 15+ technical indicators (Moving Averages, MACD, RSI, Bollinger Bands, etc.) with automated signal generation to help traders make informed decisions.

### Key Innovation

The platform's core innovation lies in its event-driven microservices architecture. Unlike traditional monolithic stock tracking applications, this system:

- **Decouples Data Collection from Processing**: Stock price updates are produced as events to Kafka, allowing multiple consumers (alert checker, analytics service, sentiment analyzer) to process the same data independently.

- **Scales Horizontally**: Each microservice can be scaled independently based on demand. The notification service can handle thousands of email alerts while the stock service continues to fetch real-time data without interference.

- **Ensures Reliability**: Kafka's message persistence guarantees that no alerts or notifications are lost, even during service disruptions.

- **Enables Real-Time Processing**: WebSocket connections provide instant updates to the frontend dashboard, creating a truly real-time user experience comparable to professional trading platforms.

## Features

### Real-Time Stock Data
The platform provides comprehensive access to live market data:
- Real-time quotes for over 1500 NSE and BSE listed stocks
- Live tracking of major market indices (NIFTY 50, SENSEX, Bank NIFTY)
- Identification of top gainers, losers, and most actively traded stocks
- Historical price data with customizable date ranges for technical analysis
- Personalized watchlists for tracking favorite stocks across sessions

### AI-Powered Sentiment Analysis
Leveraging advanced machine learning models to gauge market sentiment:
- **FinBERT Integration**: Uses a BERT model specifically fine-tuned on financial text to accurately classify news sentiment as bullish, bearish, or neutral
- **Multi-Source Aggregation**: Collects and analyzes news from various financial news APIs, RSS feeds, and financial websites
- **Trending Discovery**: Identifies stocks with unusually high sentiment activity or significant sentiment shifts
- **Historical Sentiment Tracking**: Maintains sentiment history to identify patterns and sentiment trends over time

### Technical Analysis Suite
Comprehensive technical indicators for informed trading decisions:
- **15+ Technical Indicators**: Simple Moving Average (SMA), Exponential Moving Average (EMA), Moving Average Convergence Divergence (MACD), Relative Strength Index (RSI), Bollinger Bands, Average True Range (ATR), Stochastic Oscillator, and more
- **Automated Signal Generation**: Generates trading signals ranging from Strong Buy to Strong Sell based on indicator confluence
- **Volume Analysis**: Detects unusual volume spikes and analyzes volume-price relationships
- **Stock Screener**: Multi-criteria filtering to discover stocks matching specific technical parameters
- **Market Heatmap**: Visual representation of sector performance and individual stock movements

### Alerts and Notifications System
Proactive monitoring and instant notifications:
- **Price Alerts**: Configure alerts for price movements above, below, or by a specific percentage change
- **Email Notifications**: Professionally designed HTML emails sent via Gmail SMTP with complete alert details
- **Market Timing Alerts**: Automatic notifications when NSE/BSE markets open (9:15 AM IST) and close (3:30 PM IST)
- **Daily Digest**: Morning summary email with your watchlist performance and market overview
- **Real-Time WebSocket Updates**: Instant in-app notifications without page refresh

## Architecture and Design

### System Architecture

The platform follows a microservices architecture with event-driven communication patterns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Dashboard (Frontend)              │
│              React 18 + TypeScript + Tailwind CSS            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Gateway (Backend)                │
│           Routing, Auth, CORS, WebSocket Management          │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ Stock Service │   │ Sentiment       │   │ Notification    │
│ • Live Quotes │   │ Service         │   │ Service         │
│ • History     │   │ • FinBERT       │   │ • Email Alerts  │
│ • Watchlists  │   │ • News Fetch    │   │ • WebSocket     │
└───────────────┘   └─────────────────┘   └─────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Supabase (PostgreSQL) │ Kafka (Aiven) │ Yahoo Finance API  │
└─────────────────────────────────────────────────────────────┘
```

### Architecture Components

**Frontend Layer (Next.js Dashboard)**
- Built with Next.js 16 App Router for server-side rendering and optimal performance
- TypeScript ensures type safety and better developer experience
- Tailwind CSS provides a modern, responsive UI with dark/light theme support
- Recharts library for interactive stock price charts and technical indicator visualization
- WebSocket client maintains persistent connection for real-time notifications

**API Gateway (FastAPI)**
- Serves as the unified entry point for all client requests
- Handles JWT-based authentication and authorization
- Routes requests to appropriate microservices
- Manages WebSocket connections for real-time updates
- Implements CORS policies for secure cross-origin requests
- Provides request/response caching for frequently accessed data

**Microservices Layer**

1. **Stock Service**
   - Integrates with Yahoo Finance API for real-time stock data
   - Caches frequently requested quotes to minimize API calls
   - Manages user watchlists in Supabase
   - Publishes price update events to Kafka for downstream processing

2. **Sentiment Service**
   - Fetches financial news from multiple sources
   - Processes news articles through FinBERT model for sentiment classification
   - Aggregates sentiment scores across multiple news sources
   - Identifies trending stocks based on news volume and sentiment changes
   - Stores sentiment history for pattern analysis

3. **Analytics Service**
   - Calculates technical indicators using TA-Lib and pandas
   - Generates trading signals based on indicator confluence
   - Implements stock screening with customizable filters
   - Provides volatility analysis and support/resistance levels

4. **Notification Service**
   - Monitors price alerts by consuming Kafka events
   - Sends email notifications via Gmail SMTP with HTML templates
   - Manages WebSocket connections for instant in-app notifications
   - Schedules daily digest emails and market timing alerts
   - Tracks notification delivery status

5. **User Service**
   - Handles user registration, login, and profile management
   - Integrates with Supabase for JWT token generation and validation
   - Manages user preferences and notification settings

**Data Layer**

1. **Supabase (PostgreSQL)**
   - Primary data store for users, watchlists, alerts, and historical data
   - Provides real-time subscriptions for database changes
   - Handles authentication and session management
   - Stores sentiment analysis results and technical indicator cache

2. **Apache Kafka (Aiven Cloud)**
   - Distributed event streaming platform for asynchronous communication
   - Topics for stock price updates, alert triggers, and system events
   - Ensures exactly-once delivery semantics for critical alerts
   - Enables horizontal scalability and fault tolerance

3. **External APIs**
   - Yahoo Finance API for real-time and historical stock data
   - News APIs for financial news aggregation
   - Gmail SMTP for reliable email delivery

## Technology Stack

| Layer | Technology | Purpose and Justification |
|-------|------------|---------------------------|
| **Frontend** | Next.js 16 | React framework with server-side rendering, optimized for SEO and performance |
| | TypeScript 5.0+ | Type-safe JavaScript for fewer runtime errors and better IDE support |
| | Tailwind CSS | Utility-first CSS framework for rapid UI development |
| | Recharts | Declarative charting library built on React components |
| **Backend** | FastAPI | Modern Python web framework with automatic API documentation and async support |
| | Python 3.11+ | Latest Python version with performance improvements and type hints |
| | Uvicorn | Lightning-fast ASGI server for async Python applications |
| | Pydantic | Data validation using Python type annotations |
| **Database** | Supabase | Open-source Firebase alternative with PostgreSQL and real-time subscriptions |
| | PostgreSQL | Reliable, ACID-compliant relational database |
| **Messaging** | Apache Kafka | Distributed event streaming platform for building real-time data pipelines |
| | Aiven Cloud | Managed Kafka service with SSL/TLS security |
| **AI/ML** | FinBERT | Financial domain BERT model for sentiment analysis |
| | VADER | Valence Aware Dictionary for sentiment analysis |
| | TextBlob | Simple API for common NLP tasks |
| | TA-Lib | Technical analysis library with 150+ indicators |
| | Pandas/NumPy | Data manipulation and numerical computing |
| **Email** | Gmail SMTP | Reliable email delivery with Google's infrastructure |
| **Deployment** | Render.com | Modern cloud platform with free tier for hobby projects |
| | Docker | Containerization for consistent deployments |

### Why These Technologies?

**FastAPI over Flask/Django**: FastAPI was chosen for its native async support, automatic OpenAPI documentation generation, and excellent performance. The async capabilities are crucial for handling multiple WebSocket connections and I/O-bound operations like API calls.

**Next.js over Create React App**: Next.js provides server-side rendering out of the box, which improves initial page load times and SEO. The App Router in Next.js 16 offers better code organization and data fetching patterns.

**Kafka over Redis Pub/Sub**: While Redis is faster for simple pub/sub, Kafka provides message persistence, replay capabilities, and better scalability. This is critical for financial applications where message loss is unacceptable.

**Supabase over Traditional PostgreSQL**: Supabase adds authentication, real-time subscriptions, and auto-generated REST APIs on top of PostgreSQL, significantly reducing development time while maintaining full SQL access.

**FinBERT over Generic Sentiment Models**: FinBERT is specifically trained on financial text and understands domain-specific terminology like "bearish," "bullish," "dividend yield," making it far more accurate than general-purpose sentiment models for financial news analysis.

## Getting Started

### Prerequisites

The following software and accounts are required to run the platform:

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.11 or higher | Backend runtime with latest performance improvements |
| Node.js | 20 or higher | Frontend runtime with native test runner |
| Git | Latest | Version control for cloning repository |
| Supabase Account | Free tier available | PostgreSQL database and authentication |
| Aiven Account | Free tier available | Managed Kafka for event streaming (optional) |
| Gmail Account | With 2FA enabled | Email notifications via SMTP (optional) |

### Installation Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/aditya-hubli/Real-Time-Event-Driven-Data-Platform.git
cd Real-Time-Event-Driven-Data-Platform
```

#### 2. Backend Setup

Create an isolated Python environment and install dependencies:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install all required packages
pip install -r requirements.txt
```

#### 3. Environment Configuration

Configure the application by setting up environment variables:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual credentials
# Use any text editor (notepad, vim, nano, VS Code, etc.)
```

The `.env` file should contain:

```env
# Core Configuration
SERVICE_NAME=nse-stock-tracker
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Database (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# Email Notifications (Optional)
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
SMTP_FROM_EMAIL=your-email@gmail.com

# Kafka Streaming (Optional)
KAFKA_BROKERS=your-kafka.aivencloud.com:23483
KAFKA_SECURITY_PROTOCOL=SSL
KAFKA_SSL_CA_LOCATION=ca.pem
KAFKA_SSL_CERT_LOCATION=service.cert
KAFKA_SSL_KEY_LOCATION=service.key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

#### 4. Start the Backend Server

Launch the FastAPI application:

```bash
# Run the API Gateway (main entry point)
python -m services.api_gateway
```

The API will be available at `http://localhost:8000`. You can access:
- API Documentation (Swagger): `http://localhost:8000/docs`
- Alternative Documentation (ReDoc): `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/health`

#### 5. Frontend Setup

In a new terminal window, set up the Next.js dashboard:
```bash
# Navigate to the dashboard directory
cd dashboard

# Install Node.js dependencies
npm install

# Configure frontend environment variables
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co" >> .env.local
echo "NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key" >> .env.local

# Start the development server
npm run dev
```

The dashboard will be available at `http://localhost:3000`

You now have the complete platform running locally with:
- Backend API at `http://localhost:8000`
- Frontend dashboard at `http://localhost:3000`
- Interactive API documentation at `http://localhost:8000/docs`

## API Reference

The platform exposes a comprehensive REST API with the following endpoints:

### Authentication Endpoints

Authentication uses JWT tokens provided by Supabase. All protected endpoints require the `Authorization: Bearer <token>` header.

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `POST` | `/api/v1/auth/register` | Register a new user account | No |
| `POST` | `/api/v1/auth/login` | Authenticate user and receive JWT token | No |
| `POST` | `/api/v1/auth/logout` | Invalidate current session | Yes |
| `GET` | `/api/v1/auth/me` | Get current authenticated user details | Yes |

### Stock Data Endpoints

Access real-time and historical stock market data:

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| `GET` | `/api/v1/stocks/quote/{symbol}` | Get real-time quote for a single stock | `symbol`: Stock symbol (e.g., RELIANCE.NS) |
| `GET` | `/api/v1/stocks/quotes` | Get quotes for multiple stocks | `symbols`: Comma-separated list |
| `GET` | `/api/v1/stocks/history/{symbol}` | Get historical price data | `period`: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max |
| `GET` | `/api/v1/stocks/search` | Search for stocks by name or symbol | `q`: Search query |
| `GET` | `/api/v1/stocks/market/summary` | Get NIFTY, SENSEX, and other index data | None |
| `GET` | `/api/v1/stocks/market/movers` | Get top gainers, losers, and active stocks | None |
| `GET` | `/api/v1/stocks/nse/all` | List all NSE-listed stocks | None |
| `GET` | `/api/v1/stocks/nse/sectors` | Get list of market sectors | None |

### Sentiment Analysis Endpoints

Access AI-powered sentiment analysis for stocks:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/sentiment/stock/{symbol}` | Get aggregated sentiment score and analysis |
| `GET` | `/api/v1/sentiment/trending` | Get stocks with high sentiment activity |
| `GET` | `/api/v1/sentiment/news/{symbol}` | Get news articles with sentiment scores |

### Technical Analysis Endpoints

Access technical indicators and trading signals:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/analytics/indicators/{symbol}` | Get all technical indicators (SMA, EMA, MACD, RSI, etc.) |
| `GET` | `/api/v1/analytics/signal/{symbol}` | Get overall trading signal (Strong Buy to Strong Sell) |
| `GET` | `/api/v1/analytics/analysis/{symbol}` | Get comprehensive technical analysis report |
| `POST` | `/api/v1/analytics/screener` | Screen stocks based on custom criteria |

### Alert Management Endpoints

Create and manage price alerts:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/notifications/alerts` | Create a new price alert |
| `GET` | `/api/v1/notifications/alerts` | Get all alerts for the authenticated user |
| `DELETE` | `/api/v1/notifications/alerts/{id}` | Delete a specific alert |
| `WS` | `/api/v1/notifications/ws/{user_id}` | WebSocket connection for real-time notifications |

### Email Notification Endpoints

Test and trigger email notifications:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/notifications/email/test` | Send a test email to verify SMTP configuration |
| `POST` | `/api/v1/notifications/email/price-alert` | Manually trigger a price alert email |
| `POST` | `/api/v1/notifications/email/market-open` | Send market opening notification |
| `POST` | `/api/v1/notifications/email/market-close` | Send market closing notification |
| `POST` | `/api/v1/notifications/email/daily-digest` | Send daily watchlist digest |
| `GET` | `/api/v1/notifications/email/status` | Check email service configuration status |

### Watchlist Management Endpoints

Manage personalized stock watchlists:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/stocks/watchlists/user/{user_id}` | Get all watchlists for a user |
| `POST` | `/api/v1/stocks/watchlists` | Create a new watchlist |
| `PUT` | `/api/v1/stocks/watchlists/{id}` | Update watchlist details |
| `DELETE` | `/api/v1/stocks/watchlists/{id}` | Delete a watchlist |
| `POST` | `/api/v1/stocks/watchlists/{id}/symbols/{symbol}` | Add stock to watchlist |
| `DELETE` | `/api/v1/stocks/watchlists/{id}/symbols/{symbol}` | Remove stock from watchlist |

### Interactive API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: Navigate to `http://localhost:8000/docs` for a user-friendly interface to test all endpoints
- **ReDoc**: Visit `http://localhost:8000/redoc` for detailed API documentation with request/response schemas

## Project Structure

```
Real-Time-Event-Driven-Data-Platform/
│
├── services/                      # Backend Microservices
│   ├── api_gateway.py            # Main FastAPI application entry point
│   │                             # Aggregates all service routers and handles CORS
│   │
│   ├── user_service/             # User Authentication and Management
│   │   ├── main.py              # Service initialization
│   │   ├── routes.py            # Authentication endpoints (login, register, logout)
│   │   ├── models.py            # Pydantic models for user data
│   │   └── database.py          # Supabase client for user operations
│   │
│   ├── stock_service/            # Stock Data Provider
│   │   ├── routes.py            # Stock data endpoints
│   │   ├── provider.py          # Yahoo Finance API integration
│   │   ├── nse_stocks.py        # List of all NSE stock symbols
│   │   ├── models.py            # Stock data models
│   │   └── database.py          # Watchlist database operations
│   │
│   ├── sentiment_service/        # AI Sentiment Analysis
│   │   ├── routes.py            # Sentiment analysis endpoints
│   │   ├── analyzer.py          # FinBERT model integration
│   │   ├── news_fetcher.py      # News collection from multiple sources
│   │   ├── providers.py         # News provider abstractions
│   │   └── models.py            # Sentiment data models
│   │
│   ├── analytics_service/        # Technical Analysis
│   │   ├── routes.py            # Technical analysis endpoints
│   │   ├── analyzer.py          # Technical indicator calculations
│   │   ├── calculator.py        # Trading signal generation
│   │   └── models.py            # Analytics data models
│   │
│   ├── notification_service/     # Alerts and Notifications
│   │   ├── routes.py            # Notification endpoints
│   │   ├── email_service.py     # Gmail SMTP integration and templates
│   │   ├── alert_checker.py     # Background task for monitoring price alerts
│   │   ├── websocket_manager.py # WebSocket connection management
│   │   ├── database.py          # Alert storage operations
│   │   └── models.py            # Notification data models
│   │
│   ├── order_service/            # Trading Order Management (Future)
│   │   ├── routes.py
│   │   ├── models.py
│   │   └── database.py
│   │
│   ├── payment_service/          # Payment Processing (Future)
│   │   ├── routes.py
│   │   ├── models.py
│   │   └── database.py
│   │
│   └── streaming_service/        # Kafka Event Streaming
│       ├── producer.py          # Kafka event producer
│       └── consumer.py          # Kafka event consumer
│
├── shared/                       # Shared Python Modules
│   ├── config.py                # Environment variable management
│   ├── schemas.py               # Common Pydantic schemas
│   ├── exceptions.py            # Custom exception classes
│   ├── cache.py                 # In-memory caching utilities
│   ├── events.py                # Kafka event definitions
│   └── logging_config.py        # Structured logging configuration
│
├── dashboard/                    # Next.js Frontend Application
│   ├── src/
│   │   ├── app/                 # Next.js App Router
│   │   │   ├── page.tsx         # Landing page
│   │   │   ├── layout.tsx       # Root layout with providers
│   │   │   ├── globals.css      # Global styles
│   │   │   │
│   │   │   ├── dashboard/       # Main Dashboard Pages
│   │   │   │   ├── page.tsx     # Dashboard home with market summary
│   │   │   │   ├── watchlist/   # Watchlist management
│   │   │   │   ├── analytics/   # Technical analysis view
│   │   │   │   ├── alerts/      # Price alert management
│   │   │   │   ├── sentiment/   # Sentiment analysis dashboard
│   │   │   │   ├── settings/    # User settings and preferences
│   │   │   │   └── profile/     # User profile management
│   │   │   │
│   │   │   ├── login/           # Login page
│   │   │   └── register/        # Registration page
│   │   │
│   │   ├── components/          # Reusable React Components
│   │   │   ├── layout/          # Header, Sidebar, Footer
│   │   │   ├── stocks/          # Stock cards, tables, quote displays
│   │   │   ├── charts/          # Recharts wrapper components
│   │   │   └── common/          # Buttons, modals, forms
│   │   │
│   │   ├── contexts/            # React Context Providers
│   │   │   └── AuthContext.tsx  # Authentication state management
│   │   │
│   │   ├── hooks/               # Custom React Hooks
│   │   │   └── useWebSocket.ts  # WebSocket connection hook
│   │   │
│   │   └── lib/                 # Utility Functions
│   │       ├── api.ts           # API client with fetch wrappers
│   │       └── auth.ts          # Authentication helpers
│   │
│   ├── public/                  # Static Assets
│   ├── package.json             # Node.js dependencies
│   ├── tsconfig.json            # TypeScript configuration
│   ├── tailwind.config.ts       # Tailwind CSS configuration
│   └── next.config.ts           # Next.js configuration
│
├── models/                       # Machine Learning Models
│   └── finbert/                 # FinBERT Model Files
│       ├── config.json          # Model configuration
│       ├── model.safetensors    # Model weights
│       ├── tokenizer.json       # Tokenizer configuration
│       └── vocab.txt            # Vocabulary file
│
├── infra/                        # Infrastructure as Code
│   └── supabase/
│       └── schema.sql           # PostgreSQL database schema
│
├── scripts/                      # Utility Scripts
│   └── setup_db.py              # Database initialization script
│
├── .env.example                  # Example environment variables
├── .gitignore                    # Git ignore patterns
├── requirements.txt              # Python dependencies
├── pyproject.toml                # Python project metadata
├── docker-compose.yml            # Docker services configuration
├── render.yaml                   # Render.com deployment configuration
├── Makefile                      # Development automation commands
└── README.md                     # This file
```

## Deployment Guide

### Deploying to Render.com

Render.com offers a free tier suitable for hobby projects and provides a Blueprint feature that automatically deploys multi-service applications.

#### Step 1: Prepare Your Repository

Ensure all changes are committed and pushed to GitHub:

```bash
# Stage all changes
git add -A

# Commit with descriptive message
git commit -m "Prepare for deployment"

# Push to main branch
git push origin main
```

#### Step 2: Create Render Account

1. Go to [render.com](https://render.com) and sign up using your GitHub account
2. Authorize Render to access your GitHub repositories

#### Step 3: Deploy Using Blueprint

1. In Render dashboard, click "New +" button
2. Select "Blueprint"
3. Connect your GitHub repository: `Real-Time-Event-Driven-Data-Platform`
4. Render will automatically detect the `render.yaml` file
5. Click "Apply" to create both services:
   - `stock-platform-api` (Backend Python service)
   - `stock-platform-dashboard` (Frontend Next.js service)

#### Step 4: Configure Environment Variables

In the Render dashboard, navigate to each service and add environment variables:

**For stock-platform-api (Backend):**
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Supabase Configuration
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres

# Email Notifications (Optional)
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password

# Kafka (Optional - Base64 encode certificate contents)
KAFKA_BROKERS=your-kafka.aivencloud.com:23483
KAFKA_SECURITY_PROTOCOL=SSL
KAFKA_SSL_CA=<base64-encoded-ca.pem-content>
KAFKA_SSL_CERT=<base64-encoded-service.cert-content>
KAFKA_SSL_KEY=<base64-encoded-service.key-content>

# CORS Origins (Set to your frontend URL)
CORS_ORIGINS=https://your-dashboard.onrender.com
```

**For stock-platform-dashboard (Frontend):**
```env
NEXT_PUBLIC_API_URL=https://your-api.onrender.com
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

#### Step 5: Trigger Deployment

After configuring environment variables, manually trigger a deployment or wait for automatic deployment from GitHub pushes.

### Important Notes for Production

1. **Free Tier Limitations**: 
   - Services spin down after 15 minutes of inactivity
   - First request after spin-down takes 30-60 seconds (cold start)
   - 750 hours/month of runtime per service

2. **Database**:
   - Use Supabase free tier (500MB, up to 50MB/month bandwidth)
   - No need to deploy separate database on Render

3. **SSL Certificates**:
   - Render provides automatic HTTPS with Let's Encrypt certificates
   - No manual configuration needed

4. **Monitoring**:
   - Use Render's built-in logs for debugging
   - Set up email alerts for service failures
   - Monitor Supabase dashboard for database performance

### Alternative: Docker Deployment

The project includes `docker-compose.yml` for containerized deployment:

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

This creates three containers:
- Backend API (FastAPI)
- Frontend Dashboard (Next.js)
- PostgreSQL database (if not using Supabase)

## Configuration Guide

### Required Configuration

#### Supabase Setup

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Navigate to Project Settings > API
3. Copy the following credentials:
   - Project URL (`SUPABASE_URL`)
   - Anon/Public Key (`SUPABASE_ANON_KEY`)
   - Service Role Key (`SUPABASE_SERVICE_ROLE_KEY`)
4. Go to Project Settings > Database and copy the connection string (`DATABASE_URL`)
5. Execute the SQL schema from `infra/supabase/schema.sql` in the SQL Editor

### Optional Configuration

#### Gmail SMTP Setup for Email Notifications

Gmail requires App Passwords when 2-Factor Authentication is enabled:

1. **Enable 2-Factor Authentication**:
   - Go to Google Account > Security
   - Enable 2-Step Verification

2. **Generate App Password**:
   - Go to Security > 2-Step Verification > App passwords
   - Select "Mail" and your device
   - Copy the 16-character password (format: `abcd efgh ijkl mnop`)

3. **Configure Environment Variables**:
   ```env
   EMAIL_ENABLED=true
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=abcdefghijklmnop
   SMTP_FROM_EMAIL=your-email@gmail.com
   SMTP_FROM_NAME=NSE Stock Tracker
   ```

#### Aiven Kafka Setup for Event Streaming

Kafka enables event-driven architecture for scalable real-time processing:

1. **Create Aiven Account**: Sign up at [aiven.io](https://aiven.io) (free trial available)

2. **Create Kafka Service**:
   - Select Apache Kafka
   - Choose AWS, Google Cloud, or Azure
   - Select region closest to your users (Singapore for India)
   - Choose free tier or smallest paid plan

3. **Download Certificates**:
   - Navigate to your Kafka service
   - Go to "Overview" tab
   - Download CA Certificate, Access Certificate, and Access Key
   - Save as `ca.pem`, `service.cert`, and `service.key` in project root

4. **Configure Environment Variables**:
   ```env
   KAFKA_BROKERS=your-kafka-service.aivencloud.com:23483
   KAFKA_SECURITY_PROTOCOL=SSL
   KAFKA_SSL_CA_LOCATION=ca.pem
   KAFKA_SSL_CERT_LOCATION=service.cert
   KAFKA_SSL_KEY_LOCATION=service.key
   ```

5. **For Production Deployment** (Render.com):
   Base64 encode certificate contents:
   ```bash
   # Linux/macOS
   cat ca.pem | base64 -w 0 > ca_encoded.txt
   cat service.cert | base64 -w 0 > cert_encoded.txt
   cat service.key | base64 -w 0 > key_encoded.txt
   
   # Windows PowerShell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("ca.pem")) | Out-File ca_encoded.txt
   ```
   
   Then set environment variables with encoded content:
   ```env
   KAFKA_SSL_CA=<content-of-ca_encoded.txt>
   KAFKA_SSL_CERT=<content-of-cert_encoded.txt>
   KAFKA_SSL_KEY=<content-of-key_encoded.txt>
   ```

## Testing

### Running Tests

The project includes comprehensive test coverage for all services:

```bash
# Run all tests with verbose output
pytest -v

# Run tests with coverage report
pytest --cov=services --cov=shared --cov-report=html

# Run tests for a specific service
pytest services/stock_service/tests/ -v

# Run tests with specific marker
pytest -m "unit" -v        # Run only unit tests
pytest -m "integration" -v  # Run only integration tests
```

### Test Coverage

The test suite covers:
- Unit tests for individual functions and classes
- Integration tests for API endpoints
- Service interaction tests
- Database operation tests
- WebSocket connection tests
- Email notification tests (mocked)

### Code Quality

Maintain code quality with automated tools:

```bash
# Run linter (ruff)
make lint

# Auto-format code (black + isort)
make format

# Type checking with mypy
mypy services/ shared/

# Security scan
bandit -r services/ shared/
```

## Development Workflow

### Available Make Commands

The `Makefile` provides convenient commands for common development tasks:

```bash
make install     # Install Python and Node.js dependencies
make dev         # Run development servers (backend + frontend)
make test        # Execute test suite
make lint        # Run code linters
make format      # Auto-format code
make clean       # Remove build artifacts and cache files
make docker-up   # Start Docker containers
make docker-down # Stop Docker containers
```

### Development Best Practices

1. **Branch Strategy**:
   - `main`: Production-ready code
   - `develop`: Integration branch for features
   - `feature/*`: Individual feature branches
   - `hotfix/*`: Emergency production fixes

2. **Commit Convention**:
   ```bash
   feat: Add new feature
   fix: Bug fix
   docs: Documentation changes
   style: Code formatting
   refactor: Code restructuring
   test: Adding tests
   chore: Maintenance tasks
   ```

3. **Code Review Process**:
   - All changes require pull requests
   - At least one approval before merging
   - All tests must pass
   - Code coverage should not decrease

4. **Database Migrations**:
   - Test migrations locally first
   - Document schema changes in commit message
   - Run migrations during deployment

### Debugging Tips

1. **Backend Debugging**:
   ```bash
   # Enable debug mode
   DEBUG=true python -m services.api_gateway
   
   # View detailed logs
   LOG_LEVEL=DEBUG python -m services.api_gateway
   ```

2. **Frontend Debugging**:
   ```bash
   # Run with verbose output
   npm run dev -- --debug
   
   # Build and analyze bundle size
   npm run build -- --analyze
   ```

3. **Database Queries**:
   - Use Supabase SQL Editor for direct queries
   - Enable query logging in development
   - Use pgAdmin or DBeaver for advanced debugging

## Security Considerations

The platform implements multiple security layers to protect user data and system integrity:

### Authentication and Authorization

- **JWT Tokens**: Uses JSON Web Tokens provided by Supabase for stateless authentication
- **Token Expiration**: Tokens expire after a configurable period, requiring re-authentication
- **Refresh Tokens**: Secure token refresh mechanism prevents session hijacking
- **Role-Based Access Control (RBAC)**: Different permission levels for users and administrators
- **Password Hashing**: bcrypt algorithm with salt for secure password storage (handled by Supabase)

### Data Protection

- **HTTPS Everywhere**: All communication uses TLS/SSL encryption
- **Environment Variables**: Sensitive credentials stored in environment variables, never in code
- **Secret Management**: Production secrets managed through Render's encrypted environment variables
- **SQL Injection Prevention**: Parameterized queries and ORM prevent SQL injection attacks
- **Input Validation**: Pydantic models validate all incoming data before processing
- **XSS Protection**: React automatically escapes output, preventing cross-site scripting

### API Security

- **CORS Configuration**: Whitelist of allowed origins prevents unauthorized API access
- **Rate Limiting**: Prevents abuse and DDoS attacks (configurable per endpoint)
- **Request Size Limits**: Maximum payload size prevents memory exhaustion attacks
- **Authentication Required**: Most endpoints require valid JWT token
- **API Key Rotation**: Regular rotation of API keys and secrets recommended

### Infrastructure Security

- **Kafka SSL/TLS**: All Kafka communication encrypted with mutual TLS authentication
- **Database Encryption**: Supabase encrypts data at rest and in transit
- **Firewall Rules**: Supabase provides IP whitelisting capabilities
- **Audit Logging**: All database operations logged for security audits
- **Dependency Scanning**: Regular updates to patch security vulnerabilities

### Security Best Practices

1. **Never commit secrets**: Use `.env` files and add them to `.gitignore`
2. **Rotate credentials regularly**: Change passwords, API keys, and tokens periodically
3. **Monitor logs**: Review application and database logs for suspicious activity
4. **Update dependencies**: Keep all packages updated to latest secure versions
5. **Enable 2FA**: Use two-factor authentication for all service accounts

**Aditya Hubli**
- GitHub: [@aditya-hubli](https://github.com/aditya-hubli)
- Email: aditya.m.hubli@gmail.com

## Acknowledgments

- [Yahoo Finance](https://finance.yahoo.com/) - Stock data
- [Supabase](https://supabase.com/) - Database & Auth
- [Aiven](https://aiven.io/) - Managed Kafka
- [FinBERT](https://github.com/ProsusAI/finBERT) - Sentiment model

---

