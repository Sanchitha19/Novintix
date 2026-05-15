# Design Thinking: Agentic AI Customer Support System

## Step 1: Stakeholder Pain Map

| Stakeholder | Pain Points | Impact |
|-------------|-------------|--------|
| **Customers** | Long wait times, repetitive explanations, rigid bots, unhelpful FAQs. | High churn, low CSAT, brand damage. |
| **Support Agents** | Overwhelmed by "Where is my order?" queries, manual data entry, high stress. | Burnout, high turnover, human error in complex cases. |
| **Management** | Scaling costs, lack of visibility into bot performance, inconsistent service quality. | Reduced profitability, difficulty in strategic planning. |
| **IT/Engineering** | Fragile integrations, lack of audit trails for AI decisions, "black box" model behavior. | Security risks, maintenance nightmare, compliance issues. |

## Step 2: How Might We (HMW) Statement
How might we build an intelligent, agentic support system that autonomously resolves 85% of queries with human-like empathy and precision, while ensuring 100% security compliance and real-time observability?

## Step 3: System Design Narrative
The system is built on a **Modular Agentic Architecture**. Instead of a single monolithic LLM, we use a **two-stage Orchestrator** to route queries to **Specialized Agents**. 
- **The Orchestrator** acts as the "brain," classifying intent and checking availability.
- **Specialized Agents** (Order, Refund, FAQ, Escalation) have specific toolsets and RAG contexts, allowing for high accuracy in narrow domains.
- **The Guardrail Layer** wraps all interactions, ensuring PII is masked and high-value transactions (Refunds > ₹5,000) are gated by human approval.
- **The Observability Stack** (OpenTelemetry + Grafana) provides a "flight recorder" for every decision, making the system a "white box."

## Step 4: Guardrail Justifications
- **PII Masking:** Essential for GDPR/DSARA compliance and protecting customer trust.
- **Refund Cap (₹5,000):** A critical financial control to prevent automated fraud or LLM "hallucination-driven" payouts.
- **Loop Breaker (3 hops):** Prevents infinite agent loops that drain tokens and frustrate users.
- **Sentiment-Triggered Escalation:** Ensures that frustrated customers are immediately handled by humans, preserving brand reputation.

## Step 5: Success Metrics

| Metric | Baseline | Target | Why it matters |
|--------|----------|--------|----------------|
| **Avg Resolution Time** | 6 hours | < 3 minutes | Direct correlation with customer satisfaction. |
| **FCR Rate** | 40% | > 85% | Measures the system's ability to solve problems without human intervention. |
| **Escalation Rate** | 100% | < 12% | Indicates the efficiency of the AI agents. |
| **Guardrail Violation** | N/A | < 0.1% | Measures the safety and reliability of the system. |
| **P95 Latency** | N/A | < 4s | Ensures the system feels responsive and "real-time." |
