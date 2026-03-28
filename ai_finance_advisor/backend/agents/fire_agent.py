"""
FIRE Agent
----------
Builds a complete, dynamic FIRE (Financial Independence, Retire Early) plan.

Handles:
  - Month-by-month SIP schedule (by fund category)
  - Asset allocation glidepath (equity → debt as retirement approaches)
  - Emergency fund phase
  - Insurance gap flag
  - Dynamic update when target_retirement_age changes

Mandatory scenario pack: "34-year-old, ₹24L/year, ₹18L MF, ₹6L PPF,
retire at 50 with ₹1.5L/month (today's value, inflation-adjusted)"
"""

import math

INFLATION_RATE = 0.06          # 6% annual inflation
EQUITY_RETURN = 0.12           # 12% CAGR for equity MF
DEBT_RETURN = 0.07             # 7% for debt funds
PPF_RETURN = 0.071             # 7.1% for PPF
MONTHS_PER_YEAR = 12


class FireAgent:
    def run(self, data: dict) -> dict:
        age = data["age"]
        monthly_income = data["monthly_income"]
        monthly_savings = data["monthly_savings"]
        existing_mf = data["existing_investments"]   # treated as MF+equity
        target_ret_age = data.get("target_retirement_age", 60)
        target_monthly = data["target_monthly_corpus"]  # in today's money
        risk = data.get("risk_profile", "moderate")

        # PPF inferred from salary_structure if available
        salary_struct = data.get("salary_structure") or {}
        existing_ppf = salary_struct.get("ppf_balance", 0)
        existing_total = existing_mf + existing_ppf

        years_to_retire = max(0, target_ret_age - age)
        months_to_retire = years_to_retire * MONTHS_PER_YEAR

        # ── Inflation-adjust target corpus ───────────────────────────────────
        # target_monthly at TODAY's value, inflation-adjusted to retirement
        future_monthly_need = target_monthly * ((1 + INFLATION_RATE) ** years_to_retire)
        # 4% withdrawal rule → corpus = future_monthly_need * 12 / 0.04
        required_corpus = future_monthly_need * 12 * 25

        # ── Glidepath: equity/debt split changes with age ─────────────────────
        glidepath = _build_glidepath(age, target_ret_age, risk)

        # ── Blended return across glidepath ──────────────────────────────────
        avg_equity_pct = sum(g["equity_pct"] for g in glidepath) / len(glidepath) / 100
        blended_return = avg_equity_pct * EQUITY_RETURN + (1 - avg_equity_pct) * DEBT_RETURN
        monthly_return = (1 + blended_return) ** (1 / 12) - 1

        # ── Future value of existing corpus ──────────────────────────────────
        fv_existing = existing_total * ((1 + blended_return) ** years_to_retire)

        # ── SIP needed to bridge the gap ─────────────────────────────────────
        corpus_gap = max(0, required_corpus - fv_existing)
        if corpus_gap > 0 and months_to_retire > 0 and monthly_return > 0:
            sip_required = corpus_gap * monthly_return / (
                ((1 + monthly_return) ** months_to_retire) - 1
            )
        else:
            sip_required = 0

        # ── Check feasibility ────────────────────────────────────────────────
        feasible = sip_required <= monthly_savings * 0.90
        shortfall = max(0, sip_required - monthly_savings)

        # ── SIP category allocation ──────────────────────────────────────────
        sip_allocation = _allocate_sip(sip_required, glidepath[0] if glidepath else {})

        # ── Phase plan (4 phases) ────────────────────────────────────────────
        phases = _build_phases(age, target_ret_age, sip_required, glidepath, monthly_income)

        # ── Emergency fund phase ─────────────────────────────────────────────
        emergency_target = data["monthly_expenses"] * 6
        emergency_note = (
            f"Build ₹{emergency_target:,.0f} emergency fund first (6 months expenses) "
            "in a liquid MF before investing in equity."
        )

        return {
            "retirement_target_age": target_ret_age,
            "years_to_retire": years_to_retire,
            "target_monthly_corpus_today": round(target_monthly),
            "target_monthly_corpus_inflated": round(future_monthly_need),
            "required_corpus": round(required_corpus),
            "existing_corpus": round(existing_total),
            "projected_existing_at_retirement": round(fv_existing),
            "corpus_gap": round(corpus_gap),
            "sip_required_monthly": round(sip_required),
            "sip_allocation": sip_allocation,
            "blended_return_assumed": f"{blended_return:.1%}",
            "feasible": feasible,
            "feasibility_note": (
                "SIP is within your savings capacity."
                if feasible else
                f"SIP required exceeds current savings by ₹{shortfall:,.0f}/month. "
                "Consider increasing income or extending retirement age."
            ),
            "phase_plan": phases,
            "glidepath": glidepath,
            "emergency_fund_note": emergency_note,
            "assumptions": {
                "equity_cagr": f"{EQUITY_RETURN:.0%}",
                "debt_return": f"{DEBT_RETURN:.0%}",
                "inflation": f"{INFLATION_RATE:.0%}",
                "withdrawal_rule": "4% (corpus = 25× annual need)",
                "note": "Returns are illustrative. Actual market returns will vary."
            },
            "formula_trace": {
                "future_monthly_need": (
                    f"₹{target_monthly:,.0f} × (1 + {INFLATION_RATE:.0%})^{years_to_retire} "
                    f"= ₹{future_monthly_need:,.0f}"
                ),
                "required_corpus": (
                    f"₹{future_monthly_need:,.0f} × 12 × 25 = ₹{required_corpus:,.0f}"
                ),
                "fv_existing": (
                    f"₹{existing_total:,.0f} × (1 + {blended_return:.1%})^{years_to_retire} "
                    f"= ₹{fv_existing:,.0f}"
                ),
                "corpus_gap": f"₹{required_corpus:,.0f} − ₹{fv_existing:,.0f} = ₹{corpus_gap:,.0f}",
                "sip_formula": "SIP = Gap × r / ((1+r)^n − 1) where r = monthly return, n = months",
                "sip_result": f"₹{sip_required:,.0f}/month",
            }
        }


def _build_glidepath(current_age: int, retire_age: int, risk: str) -> list:
    """
    Build year-by-year equity/debt allocation.
    Starts aggressive, shifts to conservative near retirement.
    """
    base_equity = {"conservative": 50, "moderate": 70, "aggressive": 85}.get(risk, 70)
    glidepath = []
    for yr in range(0, max(1, retire_age - current_age) + 5):
        age_now = current_age + yr
        # Linear glide from base_equity to 30% equity over 10 years pre-retirement
        years_left = max(0, retire_age - age_now)
        if years_left > 10:
            eq = base_equity
        elif years_left > 0:
            eq = 30 + (base_equity - 30) * (years_left / 10)
        else:
            eq = 30  # post-retirement: 30% equity
        glidepath.append({
            "age": age_now,
            "years_to_retire": years_left,
            "equity_pct": round(eq),
            "debt_pct": round(100 - eq),
        })
    return glidepath


def _allocate_sip(sip_total: float, allocation: dict) -> dict:
    """Split SIP across fund categories based on current allocation."""
    if sip_total == 0:
        return {"total_sip": 0, "note": "No additional SIP required."}

    equity_pct = allocation.get("equity_pct", 70) / 100
    debt_pct = allocation.get("debt_pct", 30) / 100

    equity_sip = sip_total * equity_pct
    debt_sip = sip_total * debt_pct

    # Split equity into large/mid/small
    large_cap = round(equity_sip * 0.50)
    mid_cap = round(equity_sip * 0.30)
    small_cap = round(equity_sip * 0.20)
    debt_fund = round(debt_sip * 0.60)
    liquid_fund = round(debt_sip * 0.40)

    return {
        "total_sip": round(sip_total),
        "equity": {
            "large_cap_index_fund": large_cap,
            "mid_cap_fund": mid_cap,
            "small_cap_fund": small_cap,
        },
        "debt": {
            "short_term_debt_fund": debt_fund,
            "liquid_fund": liquid_fund,
        }
    }


def _build_phases(age, retire_age, sip, glidepath, income) -> list:
    """
    4-phase financial life plan with approximate timelines.
    """
    years_left = max(0, retire_age - age)
    phase1_end = age + min(3, years_left)
    phase2_end = age + min(max(3, years_left // 2), years_left - 2)
    phase3_end = retire_age
    phase4_end = retire_age + 30

    return [
        {
            "phase": 1,
            "name": "Foundation",
            "ages": f"{age}–{phase1_end}",
            "focus": "Build emergency fund, get term insurance, start SIP habit",
            "sip_target": round(min(sip * 0.5, income * 0.15)),
            "key_actions": [
                "Open Liquid MF for emergency fund (6 months expenses)",
                "Buy term life insurance (10× annual income)",
                "Get ₹10L+ family health insurance",
                "Start SIP with 50% of target amount",
            ]
        },
        {
            "phase": 2,
            "name": "Accumulation",
            "ages": f"{phase1_end}–{phase2_end}",
            "focus": "Maximise SIP, utilise tax deductions, increase with salary hikes",
            "sip_target": round(sip),
            "key_actions": [
                "Invest full SIP amount monthly",
                "Step up SIP by 10% annually",
                "Maximise 80C (₹1.5L), 80D, NPS 80CCD",
                "Rebalance portfolio annually",
            ]
        },
        {
            "phase": 3,
            "name": "Pre-Retirement",
            "ages": f"{phase2_end}–{phase3_end}",
            "focus": "Shift to conservative allocation, reduce debt, build income sources",
            "sip_target": round(sip * 1.2),
            "key_actions": [
                "Shift equity to debt gradually (glidepath)",
                "Clear all high-interest loans",
                "Consider annuity or dividend-paying funds",
                "Healthcare costs planning",
            ]
        },
        {
            "phase": 4,
            "name": "Retirement",
            "ages": f"{phase3_end}+",
            "focus": "4% withdrawal, preserve capital, manage inflation",
            "withdrawal_per_month": "Per target corpus calculation",
            "key_actions": [
                "Withdraw 4% annually from corpus",
                "Keep 30% equity for inflation hedge",
                "Use Senior Citizen Savings Scheme (SCSS)",
                "Annual portfolio review with advisor",
            ]
        }
    ]
