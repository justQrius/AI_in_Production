# AI in Production - Experiments & Deployments

A comprehensive portfolio of experiments focused on **deploying AI agents and applications to production**. This repository demonstrates the end-to-end process of building, containerizing, and shipping autonomous systems using modern cloud infrastructure and agentic frameworks.

## 🎯 Key Skills Demonstrated

- **Production Deployment**: Containerization (Docker), Serverless (AWS Lambda, Vercel), and Infrastructure as Code (Terraform).
- **Full-Stack AI**: Building end-to-end applications with Next.js frontends and FastAPI backends.
- **Agent Orchestration**: Designing multi-agent systems with specialized roles and tool use.
- **Stateful AI**: Implementing long-term memory and persistence for conversational agents.
- **Security & Protocol**: Implementing the Model Context Protocol (MCP) and secure authentication patterns.
- **Cloud Infrastructure**: AWS (Bedrock, SageMaker, ECR), Azure, and GCP integration.

## 📚 Projects Overview

### [1. SaaS Platform: Business Idea Generator](saas_platform/)
**Focus**: Full-stack GenAI application deployment

A production-ready SaaS application that generates business ideas using LLMs, featuring real-time streaming and secure user authentication.

- **Frontend**: Next.js (Pages Router), Tailwind CSS, Clerk Auth
- **Backend**: FastAPI, OpenAI API, Server-Sent Events (SSE)
- **Deployment**: Vercel (Frontend & Backend)
- **Key Features**: Real-time token streaming, markdown rendering, protected routes

**Tech Stack**: Next.js, FastAPI, OpenAI, Clerk, Vercel

---

### [2. Digital Twin: Conversational AI](digital_twin/)
**Focus**: Stateful AI with persistence and memory

A personalized AI Digital Twin capable of maintaining long-term conversation history and mimicking a specific persona through RAG.

- **Architecture**: Decoupled frontend/backend with file-based memory persistence
- **Memory**: JSON-based session storage (extensible to Vector DBs)
- **Deployment**: Docker containerization, AWS App Runner compatible
- **Key Features**: Context retention, persona customization (`me.txt`)

**Tech Stack**: Next.js (App Router), FastAPI, Docker, Python 3.12

---

### [3. Cyber Security Agent](cyber_security_agent/)
**Focus**: Model Context Protocol (MCP) and automated analysis

An intelligent security agent leveraging **Semgrep** and the **Model Context Protocol** to perform automated code vulnerability analysis.

- **Protocol**: Implements MCP for standardized tool exposure
- **Analysis**: Semgrep engine for static code analysis
- **Infrastructure**: Terraform provisioning for Azure/GCP
- **Deployment**: Fully containerized (Docker)

**Tech Stack**: Python, Semgrep, MCP, Docker, Terraform

---

### [4. Financial Planner Agent](financial_planner_agent/)
**Focus**: Enterprise-grade multi-agent orchestration

A sophisticated multi-agent system where specialized agents (Researcher, Analyst, Writer) collaborate to produce comprehensive financial reports.

- **Orchestration**: Complex task delegation and inter-agent communication
- **RAG**: Ingestion of financial documents for grounded answers
- **Infrastructure**: AWS SageMaker for inference, Lambda for orchestration
- **Deployment**: Custom Python deployment scripts (`deploy.py`)

**Tech Stack**: AWS Bedrock, SageMaker, LangChain, Celery, Terraform

---

### [5. Autonomous Agents: Bedrock & Strands](autonomous_agents/)
**Focus**: Cloud-native autonomous agents

High-performance autonomous agents built directly on **AWS Bedrock** using the **Strands** framework, capable of complex reasoning loops and code execution.

- **Agent Capabilities**: Task planning, self-correction, tool usage
- **Tools**: Python Code Interpreter, custom logic tools
- **Deployment**: Shell script automation (`deploy.sh`) using `uv`
- **Key Features**: "Looper" agent that plans and executes multi-step tasks

**Tech Stack**: AWS Bedrock AgentCore, Strands, Python, AWS Lambda

---

## 🛠️ Technologies & Frameworks

**AI & Agents**: OpenAI (GPT-4o), AWS Bedrock (Claude 3.5 Sonnet), LangChain, Strands, AgentCore, Semgrep.

**Backend & API**: Python (FastAPI), Model Context Protocol (MCP), Server-Sent Events.

**Frontend**: React, Next.js (App & Pages Router), TypeScript, Tailwind CSS.

**DevOps & Cloud**: Docker, Kubernetes concepts, AWS (Lambda, ECR, SageMaker, App Runner), Vercel, Terraform.

**Tools**: `uv` (Python package manager), Git, VS Code/Cursor.

---

## 📊 Projects Summary

| Project | Type | Deployment | Key Tech |
|---------|------|------------|----------|
| **SaaS Platform** | Full-Stack App | Vercel | Next.js, FastAPI, Clerk |
| **Digital Twin** | Stateful Agent | Docker / App Runner | FastAPI, Memory, RAG |
| **Cyber Agent** | MCP Server | Docker / Terraform | MCP, Semgrep, Azure/GCP |
| **Financial Planner** | Multi-Agent | AWS (Lambda/SageMaker) | Bedrock, LangChain, Terraform |
| **Autonomous Agents** | Cloud Agent | AWS Bedrock | AgentCore, Strands, Python |

---

## 🚀 Getting Started

Each project is self-contained with its own `README.md` and deployment guide.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/ai-in-production.git
    cd ai-in-production
    ```

2.  **Explore a project**:
    Navigate to any project directory to see specific setup and deployment instructions.
    ```bash
    cd saas_platform
    # Follow instructions in saas_platform/README.md
    ```

3.  **Prerequisites**:
    - Docker Desktop
    - Node.js 18+
    - Python 3.10+
    - AWS CLI (for AWS projects)
    - Vercel CLI (for SaaS platform)

---

**Note**: This repository serves as a reference implementation for deploying various patterns of AI systems to production environments.