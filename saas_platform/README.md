# SaaS Platform: Business Idea Generator

A production-ready SaaS application that generates business ideas using AI, featuring secure authentication and real-time streaming.

## Features

- **AI-Powered Generation**: Uses OpenAI's GPT models to generate detailed business concepts.
- **Real-Time Streaming**: Server-Sent Events (SSE) for instant feedback and better UX.
- **Secure Authentication**: Integrated with **Clerk** for robust user management (Google, GitHub, Email).
- **Modern Frontend**: Built with **Next.js (Pages Router)**, **TypeScript**, and **Tailwind CSS**.
- **Scalable Backend**: **FastAPI** Python server handling API requests and AI orchestration.

## Tech Stack

- **Frontend**: Next.js, React, TypeScript, Tailwind CSS, Lucide Icons.
- **Backend**: Python, FastAPI, Uvicorn, OpenAI SDK.
- **Auth**: Clerk.
- **Deployment**: Vercel (Frontend & Backend).

## Project Structure

```
saas_platform/
├── backend/            # FastAPI Server
│   ├── api/            # API Endpoints
│   └── requirements.txt
└── frontend/           # Next.js Application
    ├── pages/          # Routes
    ├── styles/         # Global Styles
    └── components/     # React Components
```

## Deployment Guide

### Prerequisites
- Vercel Account
- OpenAI API Key
- Clerk Account (Publishable Key & Secret Key)

### Step 1: Environment Setup

1. **Clerk**: Create a new application in Clerk. Copy the `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`, and `CLERK_JWKS_URL`.
2. **OpenAI**: Generate a new API key.

### Step 2: Vercel Deployment

This project is configured for seamless deployment on Vercel.

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Link Project**:
   ```bash
   vercel link
   ```

3. **Configure Environment Variables**:
   ```bash
   vercel env add OPENAI_API_KEY
   vercel env add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
   vercel env add CLERK_SECRET_KEY
   vercel env add CLERK_JWKS_URL
   ```

4. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

### Step 3: Local Development

To run the project locally:

1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn api.index:app --reload
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
