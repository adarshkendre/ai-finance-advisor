"""
Test Suite — AI Money Mentor
============================
Covers all 3 mandatory Track 9 scenario pack cases + edge cases.
Run with: python tests/test_scenarios.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from orchestrator.orchestrator import Orchestrator

orc = Orchestrator()

PASS = "✅ PASS"
FAIL = "❌ FAIL"
results = []


def check(name, condition, detail=""):
    icon = PASS if condition else FAIL
    print(f"  {icon}  {name}" + (f" — {detail}" if detail else ""))
    results.append((name, condition))


def sep(title):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


# ─────────────────────────────────────────────────────────────
# SCENARIO 1: FIRE Plan (mandatory)
# 34-year-old, ₹24L/year, ₹18L MF, ₹6L PPF, retire at 50 with ₹1.5L/month
# ─────────────────────────────────────────────────────────────
sep("SCENARIO 1: FIRE Plan — Track 9 Mandatory Case")

s1 = orc.run({
    "age": 34,
    "monthly_income": 200000,
    "monthly_expenses": 80000,
    "existing_investments": 1800000,
    "salary_structure": {"ppf_balance": 600000},
    "target_retirement_age": 50,
    "target_monthly_corpus": 150000,
    "risk_profile": "moderate",
})

fire = s1.get("fire_plan", {})
check("Status is success", s1.get("status") == "success")
check("Has required_corpus", fire.get("required_corpus", 0) > 0,
      f"₹{fire.get('required_corpus', 0):,.0f}")
check("Has SIP amount", fire.get("sip_required_monthly", 0) > 0,
      f"₹{fire.get('sip_required_monthly', 0):,.0f}/month")
check("Has 4 phase plan", len(fire.get("phase_plan", [])) == 4)
check("Has glidepath", len(fire.get("glidepath", [])) > 0)
check("Has formula trace", bool(fire.get("formula_trace")))
check("Has SIP allocation by category", bool(fire.get("sip_allocation", {}).get("equity")))
check("Has inflation-adjusted target", fire.get("target_monthly_corpus_inflated", 0) > 150000,
      f"₹{fire.get('target_monthly_corpus_inflated', 0):,.0f}")
check("Has audit trail", len(s1.get("audit_trail", [])) >= 5)

# Dynamic update: change retirement age from 50 to 55
print("\n  → Dynamic update: change target_retirement_age from 50 to 55")
s1_updated = orc.run({
    "age": 34,
    "monthly_income": 200000,
    "monthly_expenses": 80000,
    "existing_investments": 1800000,
    "target_retirement_age": 55,
    "target_monthly_corpus": 150000,
    "risk_profile": "moderate",
})
fire_updated = s1_updated.get("fire_plan", {})
check("Dynamic update works", s1_updated.get("status") == "success")
check("SIP lower with longer horizon",
      fire_updated.get("sip_required_monthly", 0) < fire.get("sip_required_monthly", 1),
      f"Was ₹{fire.get('sip_required_monthly',0):,.0f}, now ₹{fire_updated.get('sip_required_monthly',0):,.0f}")


# ─────────────────────────────────────────────────────────────
# SCENARIO 2: Tax Edge Case (mandatory)
# ₹18L base, ₹3.6L HRA, ₹1.5L 80C, ₹50K NPS, ₹40K home loan interest
# ─────────────────────────────────────────────────────────────
sep("SCENARIO 2: Tax Edge Case — Track 9 Mandatory Case")

s2 = orc.run({
    "age": 35,
    "monthly_income": 150000,
    "monthly_expenses": 60000,
    "existing_investments": 1000000,
    "salary_structure": {
        "hra": 360000,
        "rent_paid": 480000,
        "city_metro": True,
        "deductions_80c": 150000,
        "nps_80ccd": 50000,
        "home_loan_interest": 40000,
        "health_insurance_80d": 25000,
    },
    "risk_profile": "moderate",
})

tax = s2.get("tax_analysis", {})
check("Status is success", s2.get("status") == "success")
check("Old regime computed", bool(tax.get("old_regime", {}).get("taxable_income", 0) > 0))
check("New regime computed", bool(tax.get("new_regime", {}).get("taxable_income", 0) > 0))
check("Has step-by-step trace (old)", len(tax.get("old_regime", {}).get("step_by_step", [])) >= 5)
check("Has step-by-step trace (new)", len(tax.get("new_regime", {}).get("step_by_step", [])) >= 3)
check("Regime recommendation provided", bool(tax.get("recommended_regime")))
check("Tax savings quantified", tax.get("tax_savings_vs_alternative", 0) >= 0,
      f"₹{tax.get('tax_savings_vs_alternative', 0):,.0f}")
check("HRA exemption in old regime trace",
      any("HRA" in step for step in tax.get("old_regime", {}).get("step_by_step", [])))
check("NPS deduction in old regime trace",
      any("NPS" in step or "80CCD" in step for step in tax.get("old_regime", {}).get("step_by_step", [])))
check("Missed deductions flagged", isinstance(tax.get("missed_deductions"), list))
check("Additional suggestions provided",
      len(tax.get("additional_tax_saving_suggestions", [])) > 0)


# ─────────────────────────────────────────────────────────────
# SCENARIO 3: Life Event — Baby
# ─────────────────────────────────────────────────────────────
sep("SCENARIO 3: Life Event — Baby (mandatory edge case)")

s3 = orc.run({
    "age": 30,
    "monthly_income": 120000,
    "monthly_expenses": 50000,
    "existing_investments": 500000,
    "life_event": "baby",
    "life_event_amount": 0,
    "risk_profile": "moderate",
})

le = s3.get("life_event_advice", {})
check("Status is success", s3.get("status") == "success")
check("Life event captured", le.get("event") == "baby")
check("Education corpus computed", bool(le.get("education_corpus", {}).get("target_corpus_in_18_years", 0) > 0),
      f"₹{le.get('education_corpus', {}).get('target_corpus_in_18_years', 0):,.0f}")
check("Monthly SIP for education", le.get("education_corpus", {}).get("monthly_sip_required", 0) > 0)
check("Insurance upgrade advice", bool(le.get("insurance_upgrade")))
check("Emergency fund upgrade", bool(le.get("emergency_fund_upgrade")))


# ─────────────────────────────────────────────────────────────
# SCENARIO 4: Error Handling & Input Validation
# ─────────────────────────────────────────────────────────────
sep("SCENARIO 4: Error Handling & Input Validation")

# Missing income
s4a = orc.run({"age": 30, "monthly_expenses": 50000, "existing_investments": 100000})
check("Missing income → needs_clarification", s4a.get("status") == "needs_clarification")
check("Missing field identified", any(f["field"] == "monthly_income" for f in s4a.get("missing_fields", [])))
check("Clarification message provided", bool(s4a.get("message")))

# Zero income
s4b = orc.run({"age": 30, "monthly_income": 0, "monthly_expenses": 50000, "existing_investments": 100000})
check("Zero income → validation error", s4b.get("status") == "needs_clarification")

# Invalid age
s4c = orc.run({"age": 150, "monthly_income": 100000, "monthly_expenses": 50000, "existing_investments": 100000})
check("Invalid age → validation error", s4c.get("status") == "needs_clarification")

# Missing everything
s4d = orc.run({})
check("Empty input → needs_clarification with all required fields",
      s4d.get("status") == "needs_clarification" and len(s4d.get("missing_fields", [])) >= 3)


# ─────────────────────────────────────────────────────────────
# SCENARIO 5: Guardrail Check
# ─────────────────────────────────────────────────────────────
sep("SCENARIO 5: Guardrail & SEBI Compliance")

s5 = orc.run({
    "age": 40,
    "monthly_income": 150000,
    "monthly_expenses": 60000,
    "existing_investments": 2000000,
    "risk_profile": "conservative",
})
advice = s5.get("final_advice", {})
check("SEBI disclaimer present", bool(advice.get("sebi_disclaimer")))
check("Tax disclaimer present", bool(advice.get("tax_disclaimer")))
check("Investment note present", bool(advice.get("investment_note")))
check("Escalation path present", bool(advice.get("escalation")))
check("Audit trail has guardrail entries",
      any(e.get("agent") == "GuardrailAgent" for e in s5.get("audit_trail", [])))


# ─────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────
sep("RESULTS SUMMARY")
passed = sum(1 for _, ok in results if ok)
total = len(results)
print(f"\n  {passed}/{total} tests passed\n")
for name, ok in results:
    print(f"  {'✅' if ok else '❌'}  {name}")

if passed < total:
    print(f"\n  ⚠️  {total - passed} test(s) failed — review output above.")
    sys.exit(1)
else:
    print("\n  🎉 All tests passed!")
