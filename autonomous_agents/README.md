# Autonomous Agents: Bedrock & Strands

A collection of high-performance autonomous agents built on **AWS Bedrock** using the **Strands** framework and **AgentCore**.

## Agents

### Looper Agent (`looper.py`)
A sophisticated agent capable of complex problem solving through:
- **Task Planning**: Breaks down problems into a todo list.
- **Tool Use**: Can manage its own tasks (create, complete, list).
- **Code Execution**: Includes a **Python Code Interpreter** to validate solutions mathematically or programmatically.
- **Reasoning Loop**: Iteratively solves problems by planning, executing, and verifying.

## Tech Stack

- **Framework**: AWS Bedrock AgentCore, Strands.
- **Infrastructure**: AWS Bedrock, AWS Lambda, Amazon ECR.
- **Language**: Python.
- **Tools**: Code Interpreter, Custom Tools.

## Deployment

This project uses `uv` for dependency management and deployment.

### Prerequisites
- AWS Credentials configured.
- Access to Claude 3 Sonnet (us-west-2 recommended).

### Deploy Command
```bash
./agents/deploy.sh
```

This script will:
1. Configure the agent infrastructure on AWS.
2. Build and push the container.
3. Launch the agent service.
