# AI Digital Twin

A personalized conversational AI that represents you, capable of remembering past conversations and answering questions based on a defined persona.

## Features

- **Long-Term Memory**: Persists conversations to JSON files, allowing the AI to recall past interactions.
- **Personality Engine**: Configurable persona (`me.txt`) to mimic specific tone, style, and knowledge.
- **RAG Capabilities**: (Retrieval Augmented Generation) Context-aware responses.
- **Modern UI**: Chat interface built with **Next.js (App Router)** and **Tailwind CSS**.

## Tech Stack

- **Frontend**: Next.js 15 (App Router), React, Tailwind CSS v4.
- **Backend**: Python, FastAPI.
- **AI**: OpenAI GPT-4o-mini.
- **Storage**: File-based JSON storage (easily extensible to Vector DBs).

## Project Structure

```
digital_twin/
├── backend/            # FastAPI Server
│   ├── server.py       # Main Application Logic
│   ├── me.txt          # Persona Definition
│   └── memory/         # Conversation Storage
└── frontend/           # Next.js App
    ├── app/            # App Router Pages
    └── components/     # Chat Interface
```

## Deployment Guide

### Option 1: Docker Deployment (Recommended)

1. **Build the container**:
   ```bash
   docker build -t digital-twin .
   ```
2. **Run the container**:
   ```bash
   docker run -p 8000:8000 -e OPENAI_API_KEY=your_key digital-twin
   ```

### Option 2: Cloud Deployment (AWS App Runner)

1. **Push to ECR**:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com
   docker tag digital-twin:latest <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/digital-twin:latest
   docker push <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/digital-twin:latest
   ```

2. **Create App Runner Service**:
   - Go to AWS App Runner console.
   - Select "Container Registry" and point to your ECR image.
   - Configure environment variables (`OPENAI_API_KEY`).
   - Deploy!

### Local Development

1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn server:app --reload
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
