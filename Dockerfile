# ADF Monitor Pro - Enterprise Container Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better layer caching)
COPY requirements_webapp.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_webapp.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs config data backup

# Create non-root user for security
RUN useradd -m -u 1000 adfmonitor && \
    chown -R adfmonitor:adfmonitor /app
USER adfmonitor

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/health || exit 1

# Default command
CMD ["python", "startup.py", "webapp", "--port", "8501"]
