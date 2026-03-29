"""
Tax Agent
---------
Computes exact Indian income tax under both Old and New regimes
using the correct FY 2024-25 tax slabs.

Handles the mandatory edge case from Track 9 scenario pack:
  - Base salary ₹18L, HRA ₹3.6L, 80C ₹1.5L, NPS ₹50K, home loan interest ₹40K
  - Must compute exact liability under both regimes
  - Must flag missed deductions
  - Must suggest 2-3 additional tax-saving instruments (ranked by liquidity & risk)

Calculations are fully traceable step-by-step.
"""

# ── FY 2024-25 Tax Slabs ─────────────────────────────────────────────────────

OLD_REGIME_SLABS = [
    (0, 250_000, 0.00),
    (250_000, 500_000, 0.05),
    (500_000, 1_000_000, 0.20),
    (1_000_000, float("inf"), 0.30),
]

NEW_REGIME_SLABS = [
    (0, 300_000, 0.00),
    (300_000, 600_000, 0.05),
    (600_000, 900_000, 0.10),
    (900_000, 1_200_000, 0.15),
    (1_200_000, 1_500_000, 0.20),
    (1_500_000, float("inf"), 0.30),
]

STANDARD_DEDUCTION_OLD = 50_000   # FY 2024-25
STANDARD_DEDUCTION_NEW = 75_000   # FY 2024-25 (budget update)
SURCHARGE_RATE = 0.10              # 10% surcharge on tax if income > 50L
HEALTH_EDU_CESS = 0.04             # 4% health & education cess


class TaxAgent:
    def run(self, data: dict) -> dict:
        monthly_income = data["monthly_income"]
        annual_income = monthly_income * 12
        salary_struct = data.get("salary_structure") or {}

        # Extract components from salary_structure
        hra = salary_struct.get("hra", 0)
        hra_rent_paid = salary_struct.get("rent_paid", 0)
        hra_city_metro = salary_struct.get("city_metro", False)
        deductions_80c = salary_struct.get("deductions_80c", 0)
        nps_80ccd = salary_struct.get("nps_80ccd", 0)
        home_loan_interest = salary_struct.get("home_loan_interest", 0)
        health_insurance_80d = salary_struct.get("health_insurance_80d", 0)
        lta = salary_struct.get("lta", 0)
        pref_regime = data.get("tax_regime_preference")

        trace_old = []
        trace_new = []

        # ── OLD REGIME ────────────────────────────────────────────────────────
        # Step 1: Gross income
        trace_old.append(f"Gross annual income: ₹{annual_income:,.0f}")

        # Step 2: Standard deduction
        taxable_old = annual_income - STANDARD_DEDUCTION_OLD
        trace_old.append(
            f"Less standard deduction: ₹{annual_income:,.0f} − ₹{STANDARD_DEDUCTION_OLD:,.0f} "
            f"= ₹{taxable_old:,.0f}"
        )

        # Step 3: HRA exemption
        hra_exempt = 0
        if hra > 0 and hra_rent_paid > 0:
            metro_pct = 0.50 if hra_city_metro else 0.40
            hra_exempt_candidates = [
                hra,
                hra_rent_paid - 0.10 * annual_income,
                annual_income * metro_pct,
            ]
            hra_exempt = max(0, min(hra_exempt_candidates))
            taxable_old -= hra_exempt
            trace_old.append(
                f"HRA exemption (min of: actual HRA ₹{hra:,.0f}, "
                f"rent − 10% salary ₹{hra_rent_paid - 0.10 * annual_income:,.0f}, "
                f"{metro_pct:.0%} of salary ₹{annual_income * metro_pct:,.0f}): "
                f"₹{hra_exempt:,.0f}"
            )

        # Step 4: 80C deduction
        actual_80c = min(deductions_80c, 150_000)
        taxable_old -= actual_80c
        trace_old.append(
            f"Section 80C deduction: ₹{actual_80c:,.0f} "
            f"(limit ₹1,50,000)"
        )

        # Step 5: NPS 80CCD(1B) additional ₹50,000
        actual_nps = min(nps_80ccd, 50_000)
        taxable_old -= actual_nps
        trace_old.append(
            f"Section 80CCD(1B) NPS: ₹{actual_nps:,.0f} (limit ₹50,000)"
        )

        # Step 6: Home loan interest (Section 24b) up to ₹2L
        hl_exempt = min(home_loan_interest, 200_000)
        taxable_old -= hl_exempt
        trace_old.append(
            f"Section 24(b) home loan interest: ₹{hl_exempt:,.0f} (limit ₹2,00,000)"
        )

        # Step 7: 80D health insurance
        actual_80d = min(health_insurance_80d, 25_000)  # basic limit
        taxable_old -= actual_80d
        trace_old.append(
            f"Section 80D health insurance: ₹{actual_80d:,.0f} (limit ₹25,000)"
        )

        taxable_old = max(0, taxable_old)
        trace_old.append(f"Taxable income (Old Regime): ₹{taxable_old:,.0f}")

        # Step 8: Compute tax
        tax_old, slab_trace_old = _compute_tax(taxable_old, OLD_REGIME_SLABS)
        trace_old.extend(slab_trace_old)

        # Step 9: Add surcharge + cess
        tax_old_final, cess_old = _add_cess_surcharge(tax_old, annual_income)
        trace_old.append(
            f"Health & Education Cess (4%): ₹{cess_old:,.0f}"
        )
        trace_old.append(
            f"Total tax payable (Old Regime): ₹{tax_old_final:,.0f}"
        )

        # ── NEW REGIME ────────────────────────────────────────────────────────
        taxable_new = annual_income - STANDARD_DEDUCTION_NEW
        trace_new.append(f"Gross annual income: ₹{annual_income:,.0f}")
        trace_new.append(
            f"Less standard deduction (New Regime): ₹{STANDARD_DEDUCTION_NEW:,.0f} → "
            f"₹{taxable_new:,.0f}"
        )
        trace_new.append(
            "Note: No other deductions (80C, HRA, 80D, home loan) are available under New Regime."
        )
        taxable_new = max(0, taxable_new)
        trace_new.append(f"Taxable income (New Regime): ₹{taxable_new:,.0f}")

        tax_new, slab_trace_new = _compute_tax(taxable_new, NEW_REGIME_SLABS)
        trace_new.extend(slab_trace_new)

        tax_new_final, cess_new = _add_cess_surcharge(tax_new, annual_income)
        trace_new.append(f"Health & Education Cess (4%): ₹{cess_new:,.0f}")
        trace_new.append(
            f"Total tax payable (New Regime): ₹{tax_new_final:,.0f}"
        )

        # ── Recommendation ────────────────────────────────────────────────────
        if pref_regime == "old":
            recommended = "Old Regime"
            savings = tax_new_final - tax_old_final
        elif pref_regime == "new":
            recommended = "New Regime"
            savings = tax_old_final - tax_new_final
        else:
            if tax_old_final < tax_new_final:
                recommended = "Old Regime"
                savings = tax_new_final - tax_old_final
            else:
                recommended = "New Regime"
                savings = tax_old_final - tax_new_final

        # ── Missed deductions analysis ────────────────────────────────────────
        missed = _find_missed_deductions(
            deductions_80c, actual_nps, health_insurance_80d,
            lta, hl_exempt, annual_income
        )

        # ── Additional tax-saving suggestions ────────────────────────────────
        suggestions = _tax_saving_suggestions(
            annual_income, data.get("risk_profile", "moderate"),
            deductions_80c, actual_nps, health_insurance_80d
        )

        return {
            "annual_income": annual_income,
            "recommended_regime": recommended,
            "tax_savings_vs_alternative": round(abs(savings)),
            "old_regime": {
                "taxable_income": round(taxable_old),
                "tax_payable": round(tax_old_final),
                "effective_rate": round(tax_old_final / annual_income * 100, 1),
                "step_by_step": trace_old,
            },
            "new_regime": {
                "taxable_income": round(taxable_new),
                "tax_payable": round(tax_new_final),
                "effective_rate": round(tax_new_final / annual_income * 100, 1),
                "step_by_step": trace_new,
            },
            "missed_deductions": missed,
            "additional_tax_saving_suggestions": suggestions,
            "disclaimer": (
                "Tax computations are based on FY 2024-25 slabs and standard provisions. "
                "Consult a qualified CA for precise filing."
            )
        }


def _compute_tax(income: float, slabs: list) -> tuple:
    tax = 0.0
    trace = []
    for lo, hi, rate in slabs:
        if income <= lo:
            break
        slab_income = min(income, hi) - lo
        slab_tax = slab_income * rate
        tax += slab_tax
        if rate > 0:
            trace.append(
                f"  ₹{lo:,.0f}–₹{min(income,hi):,.0f} @ {rate:.0%}: "
                f"₹{slab_income:,.0f} × {rate:.0%} = ₹{slab_tax:,.0f}"
            )
    trace.append(f"Base tax (before cess): ₹{tax:,.0f}")
    return tax, trace


def _add_cess_surcharge(tax: float, income: float) -> tuple:
    surcharge = tax * SURCHARGE_RATE if income > 5_000_000 else 0
    tax_after = tax + surcharge
    cess = tax_after * HEALTH_EDU_CESS
    return round(tax_after + cess), round(cess)


def _find_missed_deductions(d80c, nps, d80d, lta, hl_int, income) -> list:
    missed = []
    if d80c < 150_000:
        missed.append({
            "section": "80C",
            "unused": round(150_000 - d80c),
            "hint": "ELSS, PPF, NSC, life insurance premium, home loan principal",
        })
    if nps < 50_000:
        missed.append({
            "section": "80CCD(1B) — NPS",
            "unused": round(50_000 - nps),
            "hint": "Additional ₹50,000 deduction over 80C limit for NPS contributions",
        })
    if d80d < 25_000:
        missed.append({
            "section": "80D — Health Insurance",
            "unused": round(25_000 - d80d),
            "hint": "₹25,000 self+family; ₹50,000 if parents are senior citizens",
        })
    if lta == 0:
        missed.append({
            "section": "LTA — Leave Travel Allowance",
            "unused": "varies",
            "hint": "Claimable 2 times in a 4-year block for actual travel costs",
        })
    return missed


def _tax_saving_suggestions(income, risk, d80c, nps, d80d) -> list:
    suggestions = []

    # ELSS – moderate risk, lock-in 3 years
    if d80c < 150_000:
        suggestions.append({
            "rank": 1,
            "instrument": "ELSS (Equity Linked Savings Scheme)",
            "section": "80C",
            "max_deduction": 150_000 - d80c,
            "lock_in": "3 years",
            "risk": "Medium-High",
            "liquidity": "Low (locked for 3 years)",
            "why": "Shortest lock-in under 80C; equity returns potential; good for moderate/aggressive risk."
        })

    # NPS – low risk, long lock-in
    if nps < 50_000:
        suggestions.append({
            "rank": 2,
            "instrument": "NPS (National Pension System)",
            "section": "80CCD(1B)",
            "max_deduction": 50_000 - nps,
            "lock_in": "Until age 60",
            "risk": "Low-Medium (mix of equity/debt/government bonds)",
            "liquidity": "Very Low",
            "why": "Additional ₹50K deduction BEYOND 80C limit; employer NPS contribution also deductible."
        })

    # Health insurance – low risk, liquid
    if d80d < 25_000:
        suggestions.append({
            "rank": 3,
            "instrument": "Health Insurance Premium",
            "section": "80D",
            "max_deduction": 25_000 - d80d,
            "lock_in": "Annual",
            "risk": "Very Low",
            "liquidity": "High (annual premium)",
            "why": "Dual benefit: insurance cover + tax saving; prioritise if not insured."
        })

    # Fallback: all primary deductions maxed — suggest next tier
    if not suggestions:
        suggestions = [
            {
                "rank": 1,
                "instrument": "RBI Floating Rate Bonds / SCSS",
                "section": "No deduction — tax-efficient allocation",
                "max_deduction": "N/A",
                "lock_in": "5–7 years",
                "risk": "Very Low",
                "liquidity": "Low",
                "why": "All major deductions fully utilised. Consider tax-efficient debt for fixed income."
            },
            {
                "rank": 2,
                "instrument": "Equity Index Fund (Direct Plan) — LTCG harvesting",
                "section": "LTCG exempt up to Rs 1.25L/year",
                "max_deduction": "Up to Rs 1,25,000 LTCG tax-free annually",
                "lock_in": "None",
                "risk": "Medium-High",
                "liquidity": "High",
                "why": "Harvest Rs 1.25L gains annually tax-free. Reset cost basis to defer larger tax."
            },
            {
                "rank": 3,
                "instrument": "PPF top-up or Sukanya Samriddhi",
                "section": "80C (if any balance remains)",
                "max_deduction": "Varies",
                "lock_in": "15 years",
                "risk": "Very Low",
                "liquidity": "Very Low",
                "why": "Tax-free maturity. Ideal for long-horizon goals like child education."
            }
        ]

    return suggestions[:3]
