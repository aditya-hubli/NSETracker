FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml .

# Install Python dependencies (including NLP-ready packages)
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    pydantic \
    pydantic-settings \
    httpx \
    yfinance \
    feedparser \
    beautifulsoup4

# Future ML packages (uncomment when models are ready):
# RUN pip install --no-cache-dir \
#     torch \
#     transformers \
#     sentencepiece

# Copy shared modules
COPY shared/ ./shared/

# Copy service code
COPY services/sentiment_service/ ./services/sentiment_service/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Run the service
CMD ["uvicorn", "services.sentiment_service.main:app", "--host", "0.0.0.0", "--port", "8003"]
