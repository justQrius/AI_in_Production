# Financial Planner Agent (Alex)

A multi-agent enterprise-grade financial planning system capable of complex reasoning, data analysis, and report generation.

## Features

- **Multi-Agent Orchestration**: Coordinates multiple specialized agents (Researcher, Analyst, Writer).
- **Enterprise RAG**: Ingests and processes financial documents for context-aware answers.
- **AWS Integration**: Deployed on AWS using SageMaker, Lambda, and Bedrock.
- **Interactive Dashboard**: Next.js frontend for interacting with the agent team.

## Tech Stack

- **AI**: AWS Bedrock, SageMaker, LangChain.
- **Backend**: Python, FastAPI, Celery (for async tasks).
- **Frontend**: Next.js, Clerk Auth.
- **Infrastructure**: Terraform (AWS).

## Project Structure

```
financial_planner_agent/
├── backend/            # Multi-Agent System & Lambda Functions
├── frontend/           # Next.js Dashboard
├── terraform/          # AWS Infrastructure
├── scripts/            # Deployment Scripts (Python)
└── guides/             # Detailed Deployment Guides
```

## Deployment Guide

### Prerequisites
- AWS CLI configured with Administrator access.
- Docker installed and running.
- Node.js 18+ and Python 3.10+.
- `uv` package manager installed.

### Step 1: Infrastructure Provisioning

We use Terraform to set up the AWS environment (VPC, ECR, Lambda, SageMaker).

```bash
cd terraform
terraform init
terraform apply -auto-approve
```

### Step 2: Backend Deployment

Use the provided Python script to build and deploy the backend services.

```bash
# Install dependencies
uv sync

# Run the deployment script
uv run scripts/deploy.py
```

This script will:
1. Build Docker images for each agent.
2. Push images to Amazon ECR.
3. Update Lambda functions with new images.

### Step 3: Frontend Deployment

The frontend is a standard Next.js application.

```bash
cd frontend
npm install
npm run build
```

To deploy to Vercel:
```bash
vercel --prod
```

### Manual Verification

You can run the local test script to verify the system:
```bash
uv run scripts/run_local.py
```