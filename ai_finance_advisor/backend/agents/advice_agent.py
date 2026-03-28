"""
Advice Synthesis Agent
----------------------
Merges outputs from all specialist agents into a single, prioritised,
actionable advice document.

Rules:
  - Prioritise by urgency (critical gaps first)
  - Never give generic advice — every item is tied to a specific number
  - Deduplicate cross-agent recommendations
  - Add a "what to do this month" section
"""


class AdviceSynthesisAgent:
    def run(self, analysis: dict, fire: dict, tax: dict, life_event=None) -> dict:
        priorities = []
        action_this_month = []
        summary_lines = []

        score = analysis.get("overall_score", 50)
        dims = analysis.get("dimensions", {})
        regime = tax.get("recommended_regime", "New Regime")
        tax_savings = tax.get("tax_savings_vs_alternative", 0)
        sip = fire.get("sip_required_monthly", 0)
        feasible = fire.get("feasible", True)
        corpus_gap = fire.get("corpus_gap", 0)
        years = fire.get("years_to_retire", 0)

        # ── Summary ───────────────────────────────────────────────────────────
        summary_lines.append(
            f"Your Money Health Score is {score}/100 ({analysis.get('overall_status', '')})."
        )
        summary_lines.append(
            f"You need ₹{fire.get('required_corpus', 0):,.0f} to retire at "
            f"{fire.get('retirement_target_age', 60)} — that's in {years} years."
        )
        summary_lines.append(
            f"Switch to {regime} to save ₹{tax_savings:,.0f} in tax this year."
        )

        # ── Priority 1: Critical dimension fixes ─────────────────────────────
        for dim_name, dim_data in dims.items():
            if dim_data["score"] < 40:
                priorities.append({
                    "urgency": "Critical",
                    "dimension": dim_name.replace("_", " ").title(),
                    "score": dim_data["score"],
                    "action": dim_data.get("action", ""),
                    "amount": _extract_amount(dim_data),
                })

        # ── Priority 2: SIP setup ─────────────────────────────────────────────
        if sip > 0:
            alloc = fire.get("sip_allocation", {})
            priorities.append({
                "urgency": "High" if feasible else "High (requires income growth)",
                "dimension": "FIRE Plan — SIP",
                "action": (
                    f"Start ₹{sip:,.0f}/month SIP split as: "
                    f"Large-cap ₹{alloc.get('equity', {}).get('large_cap_index_fund', 0):,.0f}, "
                    f"Mid-cap ₹{alloc.get('equity', {}).get('mid_cap_fund', 0):,.0f}, "
                    f"Small-cap ₹{alloc.get('equity', {}).get('small_cap_fund', 0):,.0f}, "
                    f"Debt ₹{alloc.get('debt', {}).get('short_term_debt_fund', 0):,.0f}."
                ),
                "feasibility": fire.get("feasibility_note", ""),
            })

        # ── Priority 3: Tax regime switch ─────────────────────────────────────
        if tax_savings > 0:
            priorities.append({
                "urgency": "High",
                "dimension": "Tax Optimisation",
                "action": (
                    f"Switch to {regime}. You save ₹{tax_savings:,.0f} this year. "
                    f"Also: {_missed_deduction_summary(tax.get('missed_deductions', []))}"
                ),
            })

        # ── Priority 4: Attention dimensions ─────────────────────────────────
        for dim_name, dim_data in dims.items():
            if 40 <= dim_data["score"] < 60:
                priorities.append({
                    "urgency": "Medium",
                    "dimension": dim_name.replace("_", " ").title(),
                    "score": dim_data["score"],
                    "action": dim_data.get("action", ""),
                })

        # ── Life event advice injection ───────────────────────────────────────
        if life_event:
            event_name = life_event.get("event", "")
            priorities.append({
                "urgency": "High",
                "dimension": f"Life Event — {event_name.title()}",
                "action": f"See life_event_advice section for detailed {event_name} plan.",
            })

        # ── What to do THIS MONTH ─────────────────────────────────────────────
        phase1 = fire.get("phase_plan", [{}])[0]
        action_this_month = [
            phase1.get("key_actions", [None])[0] or "Review your emergency fund",
            f"Set up SIP of ₹{min(sip, fire.get('phase_plan', [{}])[0].get('sip_target', sip)):,.0f}/month in large-cap index fund",
            f"Inform HR about {regime} preference for TDS adjustment",
        ]
        if tax.get("missed_deductions"):
            first_missed = tax["missed_deductions"][0]
            unused = first_missed.get("unused", 0)
            unused_str = f"₹{unused:,.0f}" if isinstance(unused, (int, float)) else str(unused)
            instrument = (
                tax["additional_tax_saving_suggestions"][0]["instrument"]
                if tax.get("additional_tax_saving_suggestions")
                else first_missed.get("section", "80C instrument")
            )
            action_this_month.append(
                f"Utilise {first_missed['section']} ({unused_str}) via {instrument} before March 31"
            )

        return {
            "summary": " ".join(summary_lines),
            "overall_score": score,
            "priorities": priorities,
            "action_this_month": action_this_month,
        }


def _extract_amount(dim_data: dict) -> str:
    for key in ["gap", "monthly_emi", "corpus_gap"]:
        val = dim_data.get(key, 0)
        try:
            val = float(val)
            if val > 0:
                return f"₹{val:,.0f}"
        except (TypeError, ValueError):
            pass
    return ""


def _missed_deduction_summary(missed: list) -> str:
    if not missed:
        return "All major deductions are being utilised."
    sections = [m["section"] for m in missed[:2]]
    return f"Missed deductions: {', '.join(sections)} — check life_event_advice for details."
