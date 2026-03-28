"""
Analysis Agent
--------------
Computes the 6-dimension Money Health Score as specified in Track 9:
  1. Emergency Preparedness
  2. Insurance Coverage
  3. Investment Diversification
  4. Debt Health
  5. Tax Efficiency
  6. Retirement Readiness

Each dimension is scored 0-100. Overall score is weighted average.
Provides step-by-step traceable reasoning for every dimension.
"""


WEIGHTS = {
    "emergency_preparedness": 0.20,
    "insurance_coverage": 0.15,
    "investment_diversification": 0.15,
    "debt_health": 0.20,
    "tax_efficiency": 0.15,
    "retirement_readiness": 0.15,
}


class AnalysisAgent:
    def run(self, data: dict) -> dict:
        income = data["monthly_income"]
        expenses = data["monthly_expenses"]
        savings = data["monthly_savings"]
        debt_emi = data.get("debt_emi", 0)
        age = data["age"]
        existing_inv = data["existing_investments"]
        target_ret_age = data.get("target_retirement_age", 60)
        salary_struct = data.get("salary_structure") or {}

        dimensions = {}

        # ── 1. Emergency Preparedness ────────────────────────────────────────
        # Rule: 6 months of expenses should be liquid
        emergency_target = expenses * 6
        # Proxy: existing_investments * 0.2 assumed liquid (conservative estimate)
        liquid_estimate = existing_inv * 0.20
        ep_ratio = min(liquid_estimate / emergency_target, 1.0) if emergency_target > 0 else 1.0
        ep_score = round(ep_ratio * 100)
        dimensions["emergency_preparedness"] = {
            "score": ep_score,
            "status": _label(ep_score),
            "target": emergency_target,
            "estimated_liquid": round(liquid_estimate),
            "gap": max(0, round(emergency_target - liquid_estimate)),
            "reasoning": (
                f"Emergency fund target = 6 × ₹{expenses:,.0f} = ₹{emergency_target:,.0f}. "
                f"Estimated liquid savings ≈ 20% of investments = ₹{liquid_estimate:,.0f}. "
                f"Coverage ratio: {ep_ratio:.0%}."
            ),
            "action": (
                "Build a dedicated liquid emergency fund in a high-yield savings account or liquid MF."
                if ep_score < 80 else
                "Emergency fund looks healthy. Review annually."
            )
        }

        # ── 2. Insurance Coverage ────────────────────────────────────────────
        # Rule: Life cover should be ≥ 10× annual income; Health cover ≥ ₹5L
        annual_income = income * 12
        # If salary_structure provides insurance info, use it; otherwise estimate from savings rate
        has_insurance_data = "life_cover" in salary_struct or "health_cover" in salary_struct
        life_cover = salary_struct.get("life_cover", 0)
        health_cover = salary_struct.get("health_cover", 0)

        if has_insurance_data:
            life_ok = life_cover >= annual_income * 10
            health_ok = health_cover >= 500_000
            ins_score = (50 if life_ok else 20) + (50 if health_ok else 20)
        else:
            # Estimate from savings_rate heuristic
            savings_rate = savings / income if income > 0 else 0
            ins_score = 50 if savings_rate > 0.15 else 30
            life_ok = health_ok = None

        dimensions["insurance_coverage"] = {
            "score": ins_score,
            "status": _label(ins_score),
            "life_cover_provided": life_cover if has_insurance_data else "not provided",
            "health_cover_provided": health_cover if has_insurance_data else "not provided",
            "life_cover_recommended": round(annual_income * 10),
            "health_cover_recommended": 500_000,
            "reasoning": (
                f"Recommended life cover = 10 × annual income = ₹{annual_income * 10:,.0f}. "
                f"Recommended health cover = ₹5,00,000 minimum. "
                + (f"Your life cover: ₹{life_cover:,.0f} ({'✓' if life_ok else '✗'}). "
                   f"Health cover: ₹{health_cover:,.0f} ({'✓' if health_ok else '✗'})."
                   if has_insurance_data else "Insurance data not provided; provide for precise scoring.")
            ),
            "action": (
                "Get a term life cover and/or top up your health insurance."
                if ins_score < 80 else
                "Insurance coverage is adequate."
            )
        }

        # ── 3. Investment Diversification ────────────────────────────────────
        # Simple proxy: score based on savings rate & age-appropriate allocation
        savings_rate = savings / income if income > 0 else 0
        age_equity_pct = max(20, 100 - age)  # 100-age rule
        div_score = min(100, int(savings_rate * 300))  # 33%+ savings rate = 100
        # Penalise if age > 50 and no conservative shift signal
        if age > 50 and not data.get("salary_structure"):
            div_score = min(div_score, 70)

        dimensions["investment_diversification"] = {
            "score": div_score,
            "status": _label(div_score),
            "savings_rate_pct": round(savings_rate * 100, 1),
            "recommended_equity_pct": age_equity_pct,
            "recommended_debt_pct": 100 - age_equity_pct,
            "reasoning": (
                f"Savings rate: {savings_rate:.1%}. "
                f"Age-appropriate equity allocation (100−age rule): {age_equity_pct}% equity, "
                f"{100 - age_equity_pct}% debt. "
                f"Diversification score derived from savings rate and allocation guidance."
            ),
            "action": (
                f"Aim for {age_equity_pct}% equity / {100 - age_equity_pct}% debt allocation. "
                "Spread across large-cap, mid-cap, and debt funds."
                if div_score < 80 else
                "Allocation is on track. Review annually or after major life events."
            )
        }

        # ── 4. Debt Health ───────────────────────────────────────────────────
        # Rule: EMI/Income ratio should be <40%
        debt_ratio = debt_emi / income if income > 0 else 0
        if debt_ratio <= 0.10:
            dh_score = 100
        elif debt_ratio <= 0.20:
            dh_score = 80
        elif debt_ratio <= 0.30:
            dh_score = 60
        elif debt_ratio <= 0.40:
            dh_score = 40
        else:
            dh_score = 20

        dimensions["debt_health"] = {
            "score": dh_score,
            "status": _label(dh_score),
            "monthly_emi": debt_emi,
            "debt_to_income_ratio": round(debt_ratio * 100, 1),
            "safe_threshold_pct": 40,
            "reasoning": (
                f"Monthly EMI: ₹{debt_emi:,.0f}. "
                f"Debt-to-income ratio: {debt_ratio:.1%}. "
                f"Safe threshold: 40%. "
                f"{'Within safe limit.' if debt_ratio <= 0.40 else 'Above safe limit — debt is high.'}"
            ),
            "action": (
                "Debt is manageable. Continue EMI payments on schedule."
                if dh_score >= 60 else
                "Prioritise debt repayment. Consider prepaying highest-interest loan first (avalanche method)."
            )
        }

        # ── 5. Tax Efficiency ────────────────────────────────────────────────
        # Will be enriched by TaxAgent; here we compute a preliminary score
        # based on whether user is utilising 80C deductions
        deductions_80c = salary_struct.get("deductions_80c", 0)
        max_80c = 150_000
        tax_eff_score = min(100, int((deductions_80c / max_80c) * 80) + 20)

        dimensions["tax_efficiency"] = {
            "score": tax_eff_score,
            "status": _label(tax_eff_score),
            "deductions_used": deductions_80c,
            "max_80c_limit": max_80c,
            "reasoning": (
                f"80C deductions utilised: ₹{deductions_80c:,.0f} of ₹{max_80c:,.0f} limit. "
                f"Full utilisation of 80C alone improves score significantly. "
                "Detailed regime comparison computed by Tax Agent."
            ),
            "action": (
                "Maximise Section 80C (₹1.5L), explore 80D (health insurance), NPS (80CCD)."
                if tax_eff_score < 80 else
                "Tax planning looks efficient. Review after salary changes."
            )
        }

        # ── 6. Retirement Readiness ──────────────────────────────────────────
        years_to_retire = max(0, target_ret_age - age)
        # Rough check: is existing corpus on track?
        # Required corpus = monthly_expenses * 12 * 25 (4% rule, inflation-adjusted)
        required_corpus = data["target_monthly_corpus"] * 12 * 25
        # Project existing investments at 12% CAGR for years_to_retire
        projected_corpus = existing_inv * ((1.12) ** years_to_retire)
        corpus_ratio = min(projected_corpus / required_corpus, 1.5) if required_corpus > 0 else 1.0
        rr_score = min(100, int(corpus_ratio * 80))

        dimensions["retirement_readiness"] = {
            "score": rr_score,
            "status": _label(rr_score),
            "years_to_retire": years_to_retire,
            "required_corpus": round(required_corpus),
            "existing_investments": existing_inv,
            "projected_corpus_at_retirement": round(projected_corpus),
            "corpus_gap": max(0, round(required_corpus - projected_corpus)),
            "reasoning": (
                f"Required corpus (4% rule): ₹{data['target_monthly_corpus']:,.0f}/month × 12 × 25 = "
                f"₹{required_corpus:,.0f}. "
                f"Existing ₹{existing_inv:,.0f} projected at 12% CAGR for {years_to_retire} years = "
                f"₹{projected_corpus:,.0f}. "
                f"Coverage: {corpus_ratio:.0%}."
            ),
            "action": (
                f"Gap of ₹{max(0, round(required_corpus - projected_corpus)):,.0f}. "
                "Increase monthly SIP to close the gap — see FIRE Plan below."
                if rr_score < 80 else
                "Retirement corpus is on track. Review every 2 years."
            )
        }

        # ── Overall weighted score ────────────────────────────────────────────
        overall = sum(
            dimensions[dim]["score"] * weight
            for dim, weight in WEIGHTS.items()
        )
        overall = round(overall)

        return {
            "overall_score": overall,
            "overall_status": _label(overall),
            "confidence": "High" if data.get("salary_structure") else "Medium",
            "note": (
                "" if data.get("salary_structure")
                else "Provide salary_structure for higher accuracy on insurance and tax dimensions."
            ),
            "dimensions": dimensions,
        }


def _label(score: int) -> str:
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Needs Attention"
    else:
        return "Critical"
