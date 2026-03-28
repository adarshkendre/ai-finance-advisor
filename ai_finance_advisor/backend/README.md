# AI Money Mentor — ET AI Hackathon 2026 | Track 9

> **95% of Indians don't have a financial plan.** Financial advisors charge ₹25,000+/year and serve only HNIs.  
> AI Money Mentor is a multi-agent system that delivers advisor-quality financial planning to anyone with a smartphone.

---

## Architecture

```
User Input (JSON)
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR AGENT                     │
│  • Routes inputs   • Retries on failure (max 3 attempts) │
│  • Audit trail     • Detects missing fields              │
└────┬──────────┬──────────┬──────────────────────────────┘
     │          │          │
     ▼          ▼          ▼
┌─────────┐ ┌──────────┐ ┌────────┐ ┌───────────────┐
│  Input  │ │ Analysis │ │  FIRE  │ │      Tax      │
│  Agent  │ │  Agent   │ │ Agent  │ │    Agent      │
│         │ │ 6-dim    │ │ SIP+   │ │ Old vs New    │
│Validate │ │ health   │ │glide-  │ │ Real slabs    │
│& gaps   │ │ score    │ │path    │ │ Step-by-step  │
└─────────┘ └──────────┘ └────────┘ └───────────────┘
                                     ┌───────────────┐
                                     │  Life Event   │
                                     │    Agent      │
                                     │bonus/baby/    │
                                     │marriage/      │
                                     │inheritance    │
                                     └───────────────┘
     │          │          │               │
     └──────────┴──────────┴───────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  Advice Synthesis Agent │
              │  Prioritise • Merge    │
              │  Action this month     │
              └────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │    Guardrail Agent     │
              │  SEBI disclaimer       │
              │  Language check        │
              │  Escalation path       │
              └────────────────────────┘
                           │
                           ▼
              Actionable JSON Plan Output
```

**7 agents. Every decision is logged. Every calculation is traceable.**

---

## Agents & Responsibilities

| Agent | Role | Key Output |
|---|---|---|
| **Orchestrator** | Coordinates pipeline, retries, audit trail | Full audit log |
| **Input Agent** | Validates fields, asks for missing data | Normalised profile |
| **Analysis Agent** | 6-dimension Money Health Score | Score 0–100, per-dim actions |
| **FIRE Agent** | Inflation-adjusted retirement plan | SIP, glidepath, phase plan |
| **Tax Agent** | FY 2024-25 exact tax computation | Old vs New, step-by-step trace |
| **Life Event Agent** | Bonus/baby/marriage/inheritance | Event-specific action plan |
| **Guardrail Agent** | SEBI/RBI compliance enforcement | Disclaimers, escalation path |

---

## Track 9 Mandatory Scenarios — All Handled

### Scenario 1: FIRE Plan
**Input:** 34-year-old, ₹24L/year, ₹18L MF, ₹6L PPF, retire at 50 with ₹1.5L/month  
**Output:** Inflation-adjusted corpus target, month-by-month SIP plan, asset allocation glidepath  
**Dynamic:** Change `target_retirement_age` from 50→55, SIP drops proportionally

### Scenario 2: Tax Edge Case
**Input:** ₹18L salary, ₹3.6L HRA, ₹1.5L 80C, ₹50K NPS, ₹40K home loan interest  
**Output:** Exact old/new regime computation with every deduction step shown, recommendation with savings amount

### Scenario 3: Life Event
**Input:** New baby, age 30, ₹1.2L/month  
**Output:** Education corpus in 18 years, monthly SIP for education, insurance upgrade, emergency fund upgrade

---

## Setup

```bash
# 1. Clone / unzip the project
cd ai_money_mentor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
python app.py
# → http://127.0.0.1:5000
```

---

## API Reference

### `POST /analyze` — Full financial plan

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
    "deductions_80c": 100000,
    "nps_80ccd": 0,
    "home_loan_interest": 40000,
    "health_insurance_80d": 15000,
    "ppf_balance": 600000
  }
}
```

**Response includes:**
- `money_health_score` — 6-dimension score with per-dimension actions
- `fire_plan` — SIP amounts by fund category, glidepath, phase plan, formula trace
- `tax_analysis` — Step-by-step old/new regime computation, missed deductions, suggestions
- `life_event_advice` — Event-specific plan
- `final_advice` — Prioritised actions + "what to do this month"
- `audit_trail` — Every agent decision with timestamp

### `POST /update-plan` — Dynamic single-field update

```json
{
  "base_profile": { "age": 34, "monthly_income": 200000, "...": "..." },
  "change": { "field": "target_retirement_age", "value": 55 }
}
```

### `GET /scenarios` — Preloaded demo scenarios

Returns all 4 scenario pack inputs ready to POST to `/analyze`.

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Missing required field | Returns `needs_clarification` with specific field hint |
| Invalid value (age 200, income 0) | Validation error with human-readable message |
| Agent failure | Retried up to 3 times with exponential backoff |
| All retries exhausted | Graceful error with recovery suggestion |
| Audit trail | Every agent step logged with timestamp |

---

## Autonomy Depth (Judge Criteria)

**Steps completed without human input on a standard request:**

1. Input validation & gap detection
2. 6-dimension financial health scoring
3. Inflation-adjusted FIRE corpus calculation
4. Asset allocation glidepath construction
5. SIP allocation by fund category
6. Tax computation (both regimes, all deductions)
7. Missed deduction identification
8. Tax-saving instrument ranking
9. Life event handling (conditional)
10. Cross-agent advice synthesis & prioritisation
11. SEBI/RBI guardrail enforcement
12. Escalation path injection

**12 autonomous steps. 0 human inputs required after initial profile.**

---

## Impact Model

| Metric | Estimate | Assumption |
|---|---|---|
| Financial advisor cost saved | ₹25,000/year per user | vs SEBI-registered advisor minimum fee |
| Time to financial plan | 30 seconds vs 3–5 meetings | API response time vs advisor engagement cycle |
| Tax savings identified | ₹15,000–₹80,000/year | Based on average missed deductions in scenario pack |
| India addressable market | 14 crore demat accounts | SEBI data, 2024 |
| Users who can't afford advisor | ~95% of demat holders | HNI threshold ≈ ₹50L+ investible assets |

**Conservative: If 1% of ET's 50M monthly users get one tax-saving nudge worth ₹10,000 → ₹500 Cr annual value generated.**

---

## Technology Choices

| Layer | Choice | Reason |
|---|---|---|
| Framework | Flask | Lightweight, fast to demo |
| Agents | Custom Python classes | No framework overhead; logic is deterministic |
| LLM | Not required for core logic | Financial calculations are rule-based; LLM adds latency and hallucination risk for math |
| Tax slabs | Hardcoded FY 2024-25 | Accuracy over flexibility; update annually |
| Retry | In-process with backoff | Simple, auditable, no queue infrastructure needed |

> **Note:** An LLM can be added to the Advice Agent for natural-language output generation — the architecture supports it. Core calculations are intentionally rule-based for accuracy and auditability.

---

## Compliance

- All outputs include SEBI (Investment Advisers) Regulations 2013 disclaimer
- No specific BUY/SELL recommendations on named securities
- All suggestions are fund *categories*, not specific schemes
- Escalation path provided for complex situations (portfolios >₹50L, ESOP, foreign income)
- Tax calculations cite FY 2024-25 slab sources

---

## File Structure

```
ai_money_mentor/
├── app.py                        # Flask API (routes: /analyze, /update-plan, /scenarios)
├── requirements.txt
├── orchestrator/
│   └── orchestrator.py           # Central coordinator with audit trail & retry
├── agents/
│   ├── input_agent.py            # Validation, gap detection, clarification messages
│   ├── analysis_agent.py         # 6-dimension Money Health Score
│   ├── fire_agent.py             # FIRE plan: SIP, glidepath, phase plan
│   ├── tax_agent.py              # FY 2024-25 tax slabs, step-by-step trace
│   ├── life_event_agent.py       # Bonus / baby / marriage / inheritance
│   ├── advice_agent.py           # Cross-agent synthesis, prioritisation
│   └── guardrail_agent.py        # SEBI/RBI compliance enforcement
└── tests/
    └── test_scenarios.py         # 39 tests, 5 scenarios, all mandatory cases
```
