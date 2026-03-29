# AI Money Mentor — ET AI Hackathon 2026 | Track 9

> **95% of Indians don't have a financial plan.** Financial advisors charge ₹25,000+/year and serve only HNIs.
> AI Money Mentor delivers advisor-quality financial planning to anyone in under 30 seconds — completely free.

---

## What It Does

AI Money Mentor is a **multi-agent AI system** that takes your raw financial data and produces a complete, explainable financial plan covering:

| Feature | Description |
|---|---|
| **Money Health Score** | 6-dimension score (0–100) across emergency fund, insurance, diversification, debt, tax, retirement |
| **FIRE Retirement Plan** | Inflation-adjusted corpus target, monthly SIP breakdown, asset glidepath, 4-phase plan |
| **Tax Regime Optimiser** | Exact FY 2024-25 old vs new regime computation — step by step, every deduction shown |
| **Life Event Planning** | Tailored advice for bonus, new baby, marriage, or inheritance |
| **Actionable Priorities** | Top 5 ranked actions + "what to do this month" — no financial jargon |
| **SEBI Compliance** | Every output includes mandatory disclaimers and an escalation path |

---

## Live Demo — Quick Load Scenarios

The frontend includes 4 prebuilt scenarios from the Track 9 mandatory pack:

| # | Scenario | Key Input |
|---|---|---|
| 1 | **FIRE Plan** | Age 34, ₹24L/year, ₹18L MF, ₹6L PPF — retire at 50 with ₹1.5L/month |
| 2 | **Tax Optimisation** | ₹18L base, ₹3.6L HRA, ₹1.5L 80C, ₹50K NPS, ₹40K home loan interest |
| 3 | **New Baby** | Age 30, ₹1.2L/month — insurance, education corpus, protection planning |
| 4 | **Bonus Deployment** | ₹5L annual bonus — optimal deployment strategy for aggressive profile |

---

## Architecture

### System Overview

```
Browser (HTML/CSS Frontend)
         │
         ▼  HTTP POST /analyze
┌─────────────────────────────────────────────────────────┐
│                    Flask API  (port 5000)                │
│         app.py — routes, template serving               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR AGENT                      │
│  • Dispatches to 6 specialist agents in sequence        │
│  • Retries failed agents (max 2 attempts, backoff)      │
│  • Maintains a full audit trail with timestamps         │
│  • Detects missing fields and returns clarification     │
└───┬──────────┬──────────┬──────────┬────────────────────┘
    │          │          │          │
    ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌──────┐ ┌─────────┐ ┌────────────┐ ┌───────────┐
│ Input  │ │Analysis│ │ FIRE │ │  Tax    │ │ Life Event │ │ Guardrail │
│ Agent  │ │ Agent  │ │Agent │ │ Agent   │ │   Agent    │ │   Agent   │
│Validate│ │6-dim   │ │SIP + │ │Old vs   │ │bonus/baby/ │ │SEBI/RBI   │
│& gaps  │ │health  │ │glide-│ │New FY   │ │marriage/   │ │compliance │
│        │ │score   │ │path  │ │2024-25  │ │inheritance │ │disclaimer │
└────────┘ └────────┘ └──────┘ └─────────┘ └────────────┘ └───────────┘
                                    │
                                    ▼
                       ┌────────────────────────┐
                       │   Advice Synthesis     │
                       │   Prioritise & Merge   │
                       │   Action this month    │
                       └────────────────────────┘
```

### File Structure

```
ai_finance_advisor/
└── backend/                        ← PRIMARY application (production)
    ├── app.py                      ← Flask entry point — API + serves frontend
    ├── requirements.txt
    ├── templates/
    │   └── index.html              ← Full HTML/CSS dashboard (single page)
    ├── static/
    │   └── css/
    │       └── style.css           ← Complete dark-theme CSS design system
    ├── orchestrator/
    │   └── orchestrator.py         ← Central coordinator with audit trail & retry
    ├── agents/
    │   ├── input_agent.py          ← Validation, gap detection, clarification
    │   ├── analysis_agent.py       ← 6-dimension Money Health Score (0–100)
    │   ├── fire_agent.py           ← FIRE plan: SIP, glidepath, phase plan
    │   ├── tax_agent.py            ← FY 2024-25 tax slabs, step-by-step trace
    │   ├── life_event_agent.py     ← Bonus / baby / marriage / inheritance
    │   ├── advice_agent.py         ← Cross-agent synthesis & prioritisation
    │   └── guardrail_agent.py      ← SEBI/RBI compliance enforcement
    ├── utils/
    └── tests/
        └── test_scenarios.py       ← Automated test scenarios

backend/                            ← Simpler service-based version (reference only)
```

---

## Installation & Setup

### Prerequisites

- **Python 3.10 or higher**
- **pip** (comes with Python)

---

### Windows

```cmd
:: 1. Clone the repository
git clone <your-repo-url>
cd <repo-folder>

:: 2. (Recommended) Create a virtual environment
python -m venv venv
venv\Scripts\activate

:: 3. Install dependencies
pip install flask flask-cors anthropic python-dotenv gunicorn

:: 4. Navigate to the backend
cd ai_finance_advisor\backend

:: 5. Run the development server
python app.py
```

Open your browser and go to: **http://127.0.0.1:5000**

**Windows — stop the server:** Press `Ctrl + C` in the terminal.

> **Note:** If `python` is not recognised, try `py` instead of `python`.

```cmd
:: Alternative if 'python' command not found
py -m venv venv
venv\Scripts\activate
pip install flask flask-cors anthropic python-dotenv gunicorn
cd ai_finance_advisor\backend
py app.py
```

---

### macOS / Linux

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd <repo-folder>

# 2. (Recommended) Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install flask flask-cors anthropic python-dotenv gunicorn

# 4. Navigate to the backend
cd ai_finance_advisor/backend

# 5. Run the development server
python app.py
```

Open your browser and go to: **http://127.0.0.1:5000**

**Stop the server:** Press `Ctrl + C` in the terminal.

---

### Production (All Platforms — using Gunicorn)

Gunicorn is recommended for production deployments. Not available natively on Windows — use WSL2 or Docker on Windows.

```bash
# From the repository root
gunicorn --bind 0.0.0.0:5000 --reuse-port --chdir ai_finance_advisor/backend app:app

# With multiple workers (recommended for production)
gunicorn --bind 0.0.0.0:5000 --workers 4 --chdir ai_finance_advisor/backend app:app
```

---

### Docker (Cross-platform)

```bash
# Build image
docker build -t ai-money-mentor .

# Run container
docker run -p 5000:5000 ai-money-mentor

# Then open: http://localhost:5000
```

---

### Verify the Server is Running

```bash
# Health check (works on Windows PowerShell, macOS, Linux)
curl http://127.0.0.1:5000/health

# Expected response:
# {"agents": 7, "status": "ok"}
```

On **Windows Command Prompt**, if `curl` is unavailable, use PowerShell:

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:5000/health | Select-Object -ExpandProperty Content
```

---

## Using the Frontend

Once the server is running, open **http://127.0.0.1:5000** in your browser.

1. **Quick Load** — Click any scenario card to auto-fill the form and run analysis instantly
2. **Manual Entry** — Fill in your financial profile and click **Analyse My Finances**
3. **View Results** — Scroll through your full financial plan including score, FIRE plan, tax comparison, and priorities

---

## API Reference

### `GET /health`

```json
{ "status": "ok", "agents": 7 }
```

### `GET /scenarios`

Returns 4 prebuilt demo scenarios with full input payloads.

---

### `POST /analyze` — Full Financial Analysis

**Request:**

```json
{
  "age": 34,
  "monthly_income": 200000,
  "monthly_expenses": 80000,
  "existing_investments": 1800000,
  "target_retirement_age": 50,
  "target_monthly_corpus": 150000,
  "risk_profile": "moderate",

  "debt_emi": 0,

  "life_event": "bonus",
  "life_event_amount": 500000,

  "salary_structure": {
    "hra": 360000,
    "rent_paid": 480000,
    "city_metro": true,
    "deductions_80c": 150000,
    "nps_80ccd": 50000,
    "home_loan_interest": 40000,
    "health_insurance_80d": 25000,
    "ppf_balance": 600000
  }
}
```

**Required fields:** `age`, `monthly_income`, `monthly_expenses`, `existing_investments`

**Optional fields:** all others (sensible defaults applied)

**`risk_profile` values:** `conservative` | `moderate` | `aggressive`

**`life_event` values:** `bonus` | `baby` | `marriage` | `inheritance`

---

**Response structure:**

```json
{
  "status": "success",
  "processing_time_sec": 0.012,

  "money_health_score": {
    "overall_score": 63,
    "overall_status": "Good",
    "dimensions": {
      "emergency_preparedness": { "score": 45, "status": "Fair", "reasoning": "...", "action": "..." },
      "insurance_coverage":     { "score": 20, "status": "Needs Work", "reasoning": "...", "action": "..." },
      "investment_diversification": { "score": 72, "status": "Good", "reasoning": "...", "action": "..." },
      "debt_health":            { "score": 100, "status": "Excellent", "reasoning": "...", "action": "..." },
      "tax_efficiency":         { "score": 20, "status": "Needs Work", "reasoning": "...", "action": "..." },
      "retirement_readiness":   { "score": 55, "status": "Fair", "reasoning": "...", "action": "..." }
    }
  },

  "fire_plan": {
    "retirement_target_age": 50,
    "years_to_retire": 16,
    "required_corpus": 87500000,
    "sip_required_monthly": 239059,
    "projected_existing_at_retirement": 12500000,
    "corpus_gap": 75000000,
    "feasible": false,
    "sip_allocation": {
      "equity": { "large_cap_index_fund": 85763, "mid_cap_fund": 51458, "small_cap_fund": 34305 },
      "debt":   { "liquid_fund": 29405, "short_term_debt_fund": 44107 },
      "total_sip": 245038
    },
    "phase_plan": [ { "phase": "Accumulation", "years": "2026–2030", "equity_pct": 70, "debt_pct": 30, "key_actions": ["..."] } ]
  },

  "tax_analysis": {
    "annual_income": 2400000,
    "recommended_regime": "new",
    "tax_savings_vs_alternative": 124800,
    "old_regime": { "taxable_income": 1820000, "tax_payable": 538200, "effective_rate": 22.4 },
    "new_regime": { "taxable_income": 2325000, "tax_payable": 413400, "effective_rate": 17.2 },
    "missed_deductions": [ { "section": "80D", "description": "Health insurance premium", "unused": 25000 } ],
    "additional_tax_saving_suggestions": [ { "instrument": "NPS Tier 1", "max_limit": 50000, "why": "Additional 80CCD(1B) deduction in Old Regime" } ]
  },

  "life_event_advice": { },

  "final_advice": {
    "overall_score": 63,
    "summary": "Your finances are in good shape with clear room to optimise...",
    "priorities": [
      { "rank": 1, "urgency": "Critical", "dimension": "Tax Efficiency", "action": "Switch to New Regime — saves ₹1,24,800/year", "amount": "₹1,24,800" }
    ],
    "action_this_month": [
      "Open Liquid MF for emergency fund (6 months expenses)",
      "Set up SIP of ₹30,000/month in large-cap index fund",
      "Inform HR about New Regime preference for TDS adjustment"
    ],
    "sebi_disclaimer": "IMPORTANT: This output is generated by an AI model and is for informational and educational purposes only...",
    "tax_disclaimer": "Tax computations are based on publicly available Indian tax laws. Consult a qualified Chartered Accountant for accurate tax filing."
  },

  "audit_trail": [
    { "agent": "InputAgent",    "status": "success", "timestamp": "2026-03-29T10:00:00" },
    { "agent": "AnalysisAgent", "status": "success", "timestamp": "2026-03-29T10:00:00" }
  ]
}
```

---

### `POST /update-plan` — Dynamic Single-Field Update

Re-runs the full pipeline after changing one field (e.g., push retirement age from 50 to 55).

**Request:**

```json
{
  "base_profile": {
    "age": 34,
    "monthly_income": 200000,
    "monthly_expenses": 80000,
    "existing_investments": 1800000
  },
  "change": {
    "field": "target_retirement_age",
    "value": 55
  }
}
```

**Response:** Same as `/analyze` plus `"change_applied": { "target_retirement_age": 55 }`

---

### Error Responses

| Scenario | HTTP | Response |
|---|---|---|
| Missing required field | 400 | `{ "status": "incomplete", "missing_fields": [...], "clarification": "..." }` |
| Invalid value | 400 | `{ "error": "...", "detail": "..." }` |
| Agent pipeline failure | 500 | `{ "error": "Agent pipeline failure", "detail": "...", "recovery": "..." }` |

---

## Agents — Detailed Responsibilities

| Agent | Input | Output | Key Logic |
|---|---|---|---|
| **Orchestrator** | Raw JSON | Coordinated result | Dispatch, retry (max 2), audit trail |
| **Input Agent** | Raw dict | Validated profile | Required/optional field checks, cross-field validation |
| **Analysis Agent** | Validated profile | 6 dimension scores | Weighted average (emergency 20%, debt 20%, others 15%) |
| **FIRE Agent** | Validated profile | Retirement plan | 4% rule, inflation @ 6%, equity/debt glidepath, SIP formula |
| **Tax Agent** | Validated profile | Old vs New comparison | FY 2024-25 slabs, HRA triple-min, 80C/80D/80CCD deductions |
| **Life Event Agent** | Validated profile | Event action plan | Rule-based by event type |
| **Advice Agent** | All agent outputs | Priorities + actions | Cross-agent synthesis, urgency ranking |
| **Guardrail Agent** | Advice dict | Compliant output | SEBI disclaimer injection, blocked pattern scan |

---

## Calculation Methodology

### FIRE Corpus Formula

```
Future monthly need  = target_monthly_corpus × (1 + 6%)^years_to_retire
Required corpus      = future_monthly_need × 12 × 25   (4% withdrawal rule)
FV of existing       = existing_investments × (1 + blended_return)^years
Corpus gap           = required_corpus − FV of existing
Monthly SIP          = corpus_gap × r / ((1+r)^n − 1)   where r = monthly blended return
```

### Blended Return (Glidepath)

```
Age < 40:  Equity 80% / Debt 20%  → blended ≈ 11%
Age 40–50: Equity 60% / Debt 40%  → blended ≈ 10%
Age > 50:  Equity 40% / Debt 60%  → blended ≈ 9%

Equity CAGR = 12%  |  Debt return = 7%  |  PPF = 7.1%
```

### Tax Calculation (FY 2024-25)

**Old Regime slabs:**

| Income Range | Rate |
|---|---|
| Up to ₹2.5L | 0% |
| ₹2.5L – ₹5L | 5% |
| ₹5L – ₹10L | 20% |
| Above ₹10L | 30% |

Standard deduction: ₹50,000 | 4% health & education cess | 10% surcharge above ₹50L

**New Regime slabs (FY 2024-25):**

| Income Range | Rate |
|---|---|
| Up to ₹3L | 0% |
| ₹3L – ₹6L | 5% |
| ₹6L – ₹9L | 10% |
| ₹9L – ₹12L | 15% |
| ₹12L – ₹15L | 20% |
| Above ₹15L | 30% |

Standard deduction: ₹75,000 | 4% cess

---

## Autonomy Depth

**12 autonomous steps completed without human input on every request:**

1. Input validation & cross-field checks
2. Gap detection & clarification message generation
3. Emergency fund assessment
4. Insurance coverage estimation
5. Investment diversification scoring
6. Debt health calculation
7. Tax efficiency assessment
8. Retirement readiness scoring
9. Inflation-adjusted corpus calculation + SIP derivation
10. Asset glidepath construction (phase plan)
11. Old vs New tax regime comparison (all deductions)
12. Cross-agent advice synthesis, prioritisation & SEBI compliance enforcement

---

## Technology Stack

| Layer | Technology | Reason |
|---|---|---|
| Language | Python 3.12 | Stable, readable financial logic |
| Web Framework | Flask + flask-cors | Lightweight, fast, minimal overhead |
| Frontend | HTML + CSS (no JS framework) | Fast load, zero dependencies, works everywhere |
| Agent Pattern | Custom Python classes | No framework overhead; fully traceable deterministic logic |
| Tax Logic | Hardcoded FY 2024-25 slabs | Accuracy over flexibility — update annually |
| Retry Strategy | In-process exponential backoff | Simple, auditable, no queue infrastructure needed |
| Production Server | Gunicorn | WSGI-compliant, multi-worker |

> **LLM note:** The core financial calculations are intentionally rule-based for accuracy and auditability. The `anthropic` SDK is available in the environment and can be wired into the Advice Agent for natural-language narrative generation without changing any other agent.

---

## Compliance & Disclaimers

- All outputs include the mandatory **SEBI (Investment Advisers) Regulations 2013** disclaimer
- No specific BUY/SELL recommendations on named securities — all suggestions are fund *categories*
- Tax calculations cite FY 2024-25 slab sources and include a CA disclaimer
- Escalation path provided for complex situations (portfolio > ₹50L, ESOPs, foreign income)
- Guardrail agent scans for blocked patterns before every response

---

## Impact Model

| Metric | Estimate | Source |
|---|---|---|
| Financial advisor cost saved | ₹25,000/year per user | vs SEBI-registered advisor minimum fee |
| Time to financial plan | 30 seconds vs 3–5 meetings | API response vs advisor engagement cycle |
| Tax savings identified | ₹15,000–₹80,000/year | Average missed deductions in scenario pack |
| India addressable market | 14 crore demat accounts | SEBI data, 2024 |
| Users without an advisor | ~95% of demat holders | HNI threshold ≈ ₹50L+ investible assets |

**Conservative projection:** If 1% of ET's 50M monthly users receive one tax-saving nudge worth ₹10,000 → **₹500 Cr annual value generated.**

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `python` not recognised on Windows | Use `py` instead of `python` |
| `pip` not recognised | Run `python -m pip install ...` or `py -m pip install ...` |
| Port 5000 already in use | Change port: `python app.py` then edit `app.run(port=5001)` in `app.py` |
| `ModuleNotFoundError: flask` | Make sure your virtual environment is activated before running |
| Blank page in browser | Check the terminal for error output; ensure you are in the `ai_finance_advisor/backend` directory |
| Windows venv activation fails | Run as Administrator or use `Set-ExecutionPolicy RemoteSigned` in PowerShell |

---

## License

This project was built for the **ET AI Hackathon 2026 — Track 9** and is intended for educational and demonstration purposes.
