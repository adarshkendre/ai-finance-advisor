# AI Money Mentor — Backend

This is the primary application. See the [root README](../../README.md) for full documentation, Windows setup instructions, API reference, and architecture details.

## Quick Start

### Windows

```cmd
cd ai_finance_advisor\backend
python app.py
```

### macOS / Linux

```bash
cd ai_finance_advisor/backend
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## Agents

| Agent | File | Role |
|---|---|---|
| Orchestrator | `orchestrator/orchestrator.py` | Coordinates all agents, handles retries and audit trail |
| Input Agent | `agents/input_agent.py` | Validates and normalises user input |
| Analysis Agent | `agents/analysis_agent.py` | Computes 6-dimension Money Health Score |
| FIRE Agent | `agents/fire_agent.py` | Calculates retirement corpus, SIP, and glidepath |
| Tax Agent | `agents/tax_agent.py` | FY 2024-25 Old vs New regime comparison |
| Life Event Agent | `agents/life_event_agent.py` | Advice for bonus, baby, marriage, inheritance |
| Advice Agent | `agents/advice_agent.py` | Synthesises all agent outputs into priorities |
| Guardrail Agent | `agents/guardrail_agent.py` | Enforces SEBI/RBI compliance |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | HTML frontend dashboard |
| GET | `/health` | Health check |
| GET | `/api/info` | API metadata |
| POST | `/analyze` | Full financial analysis |
| POST | `/update-plan` | Re-run with one changed field |
| GET | `/scenarios` | Prebuilt demo scenarios |
