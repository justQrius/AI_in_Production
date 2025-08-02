# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy requirements
COPY backend/requirements.txt .

# Install dependencies
RUN uv pip install --system -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy personality
COPY backend/me.txt .

# Create memory directory
RUN mkdir -p ../memory

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
