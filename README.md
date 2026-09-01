# AgentCart: Autonomous B2B Commerce & Payment Agent

AgentCart is an enterprise-grade merchant integration layer built for Razorpay Test-Mode APIs, designed to bridge external AI buyer agents with merchant inventories securely, with hard financial bounds, cryptographic UAP security, agent-to-agent negotiations, webhook notifications, immutable audit trails, and graceful failure handling.

## Track Selection
* Track 01: AI Growth & Agentic Commerce

## Key Features
* NPCI UAP Protocol Security: Strict cryptographic verification utilizing HMAC-SHA256 token signing and custom X-UAP-Agent-Token header authentication.
* Agent-to-Agent (A2A) Negotiation Engine: Margin-aware dynamic pricing loop allowing AI buyer agents to propose custom discounts evaluated against merchant floor limits in real time (/agent/negotiate).
* Event-Driven Architecture: Signed webhook dispatcher for secure payload notifications and automated flash campaign orchestration (/agent/campaigns).
* Agent-Readable Catalog API: Exposes clean structured JSON endpoints (/catalog) for programmatic discovery.
* Bounded Financial Guardrails: Enforces strict spending limits (e.g., max 5000 INR per session) to block unauthorized or rogue API requests.
* Immutable Audit Trail: Logs every successful, negotiated, or blocked transaction securely into audit_trail.json (/audit/logs).
* Graceful Failure Recovery: Catches missing products, out-of-stock items, and gateway drops, rolling back state safely without crashing.

## Tech Stack
* Python & FastAPI: High-performance asynchronous backend framework.
* Razorpay Python SDK: Live test-mode payment gateway integration.
* Pydantic: Robust data validation and payload safety.
* SQLite & SQLAlchemy: Persistent relational inventory and session management.
* HMAC-SHA256 & Requests: Cryptographic verification and event-driven webhook dispatching.

## Quick Setup & Installation
1. Clone or open the project workspace in your terminal.
2. Install dependencies:
   pip install fastapi uvicorn sqlalchemy pydantic requests razorpay
3. Initialize and run the server:
   uvicorn main:app --reload
4. Access the interactive Swagger documentation at: http://127.0.0.1:8000/docs

## API Endpoints Reference

* GET /
  * Security: Public
  * Description: Returns node health status, versioning, and system availability.

* GET /catalog
  * Security: Public
  * Description: Fetches real-time SQLite inventory, pricing, and stock levels for AI buyer discovery.

* POST /agent/checkout
  * Security: X-UAP-Agent-Token Header Required
  * Description: Processes autonomous cart checkout, bundle discounts, guardrails, and Razorpay orders.

* POST /agent/campaigns
  * Security: X-UAP-Agent-Token Header Required
  * Description: Triggers the automated flash campaign orchestrator for AI buyers.

* POST /agent/negotiate
  * Security: X-UAP-Agent-Token Header Required
  * Description: Evaluates AI agent counter-offer discounts against merchant margin floors.

* GET /audit/logs
  * Security: Public
  * Description: Retrieves the complete chronological enterprise audit trail ledger.
