# Cyber Security Agent

An intelligent security agent leveraging **Semgrep** and **OpenAI Agents SDK** with **Model Context Protocol (MCP)** for automated code vulnerability analysis.

## Features

- **AI-Powered Analysis**: Uses OpenAI's agent framework to analyze Python code for security vulnerabilities
- **Semgrep Integration**: Leverages industry-standard static analysis via Semgrep MCP server
- **Cloud Deployment**: Optimized for Azure Container Apps and Google Cloud Run
- **Modern Stack**: Next.js (TypeScript) frontend with FastAPI backend

## Tech Stack

- **Frontend**: Next.js 15, React, TypeScript, Tailwind CSS
- **Backend**: Python 3.12, FastAPI, OpenAI Agents SDK
- **Analysis**: Semgrep (via MCP server)
- **Infrastructure**: Terraform, Docker
- **Cloud**: Azure Container Apps, Google Cloud Run (planned)

## Project Structure

```
cyber_security_agent/
├── backend/            # FastAPI Server with MCP Integration
│   ├── server.py       # Main API server
│   ├── context.py      # Agent context management
│   └── mcp_servers.py  # MCP server configuration
├── frontend/           # Next.js Static Export
├── terraform/          # Infrastructure as Code
├── Dockerfile          # Single-stage container build
└── airline.py          # Example vulnerable application
```

## Deployment Guide

### Prerequisites
- Docker Desktop
- Azure CLI (for Azure deployment)
- Terraform
- Environment variables: `OPENAI_API_KEY`, `SEMGREP_APP_TOKEN`

### Local Development

```bash
# Backend
cd backend
uv run server.py

# Frontend (separate terminal)
cd frontend
npm run dev
```

### Docker Deployment

```bash
# Build
docker build -t cyber-analyzer .

# Run
docker run --rm -d \
  --name cyber-analyzer \
  -p 8000:8000 \
  --env-file .env \
  cyber-analyzer

# View logs
docker logs cyber-analyzer
```

### Cloud Deployment (Azure)

```bash
cd terraform
terraform init
terraform workspace select azure
terraform apply
```

**Important**: Semgrep requires at least **2GB RAM** in cloud environments for rule registry loading.

## Technical Details

### Docker Architecture
- Single-stage build serving both API and static frontend
- Frontend built as Next.js static export
- FastAPI serves both `/api/*` endpoints and static files
- Runs on port 8000

### MCP Configuration
- Uses MCP 1.12.2 (pinned for compatibility)
- Semgrep MCP server launched via `uvx`
- Handles tool calls for code analysis

### Known Limitations
- Requires 2GB+ memory allocation (cloud deployment)
- MCP version pinned to 1.12.2 for stability

## API Endpoints

- `POST /api/analyze` - Analyze Python code for vulnerabilities
- `GET /health` - Health check endpoint
- `/` - Static frontend