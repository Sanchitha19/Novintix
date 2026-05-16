# Novintix AI Support System — Hackathon UI

This is the production-grade React frontend for the Novintix Agentic AI Support System. It features a split-screen layout with a customer chat interface and a live admin monitoring dashboard.

## 🚀 Getting Started

### 1. Prerequisites
- Node.js (v16+)
- npm or yarn
- FastAPI Backend running on port 8000

### 2. Installation
```bash
cd frontend
npm install
```

### 3. Running the Frontend
```bash
npm run dev
```
The app will be available at `http://localhost:3000` (or `http://localhost:5173` depending on Vite default).

### 4. Running the Backend
Ensure your FastAPI server is running:
```bash
python main.py
```

## 🛠 Features

### Customer Chat (Left Panel)
- **JWT Authentication**: Login with demo credentials to start.
- **Agent Awareness**: Each AI response identifies which specialized agent (Tracking, Refund, FAQ, Escalation) handled the query.
- **Guardrail Visibility**: Live indicators for PII masking and refund limits.
- **Traceability**: Monospace trace IDs on every response for audit trails.

### Admin Dashboard (Right Panel)
- **System Health**: Real-time operational status and latency monitoring.
- **Interactive Charts**: Recharts-powered query volume and intent distribution.
- **Live Event Log**: A terminal-style feed of system transitions (Routing, Tool Calls, RAG, Guardrails).
- **Agent Cluster**: Monitor individual agent performance and confidence scores.

## 🔑 Demo Credentials
- **Username**: `johnd`
- **Password**: `m38mzuvjxl`

---
*Built for the Novintix Hackathon — 2026*
