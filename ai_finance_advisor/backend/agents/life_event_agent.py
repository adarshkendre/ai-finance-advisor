"""
Life Event Agent
----------------
Handles life-event-triggered financial decisions:
  - bonus       : lump-sum investment strategy
  - marriage    : joint planning, HRA optimisation, combined insurance
  - baby        : education corpus planning, increased insurance, emergency fund
  - inheritance : windfall management, tax implications

Customised to user's tax bracket, portfolio, risk profile.
"""


class LifeEventAgent:
    def run(self, data: dict) -> dict:
        event = data.get("life_event")
        amount = float(data.get("life_event_amount", 0))
        risk = data.get("risk_profile", "moderate")
        annual_income = data["monthly_income"] * 12
        monthly_expenses = data["monthly_expenses"]
        age = data["age"]
        salary_struct = data.get("salary_structure") or {}

        handlers = {
            "bonus": self._handle_bonus,
            "marriage": self._handle_marriage,
            "baby": self._handle_baby,
            "inheritance": self._handle_inheritance,
        }

        handler = handlers.get(event)
        if not handler:
            return {
                "event": event,
                "error": f"Unrecognised life event '{event}'. "
                         "Valid events: bonus, marriage, baby, inheritance."
            }

        result = handler(amount, risk, annual_income, monthly_expenses, age, salary_struct, data)
        result["event"] = event
        result["disclaimer"] = (
            "Life event advice is illustrative. Consult a SEBI-registered advisor "
            "and CA before making investment or tax decisions."
        )
        return result

    def _handle_bonus(self, amount, risk, annual_income, expenses, age, salary, data):
        # Optimal bonus deployment strategy
        emergency_gap = max(0, expenses * 6 - data["existing_investments"] * 0.2)
        tax_saving_headroom = max(0, 150_000 - salary.get("deductions_80c", 0))

        # Prioritise: emergency fund → tax saving → investments
        alloc = []
        remaining = amount

        if emergency_gap > 0 and remaining > 0:
            fill = min(emergency_gap, remaining)
            alloc.append({"priority": 1, "use": "Top up emergency fund", "amount": round(fill),
                          "instrument": "Liquid MF / High-yield savings account"})
            remaining -= fill

        if tax_saving_headroom > 0 and remaining > 0:
            fill = min(tax_saving_headroom, remaining)
            alloc.append({"priority": 2, "use": "80C tax saving", "amount": round(fill),
                          "instrument": "ELSS (lock-in 3 yrs) or PPF"})
            remaining -= fill

        if remaining > 0:
            eq = {"conservative": 0.40, "moderate": 0.65, "aggressive": 0.80}.get(risk, 0.65)
            eq_amt = round(remaining * eq)
            debt_amt = round(remaining * (1 - eq))
            alloc.append({"priority": 3, "use": "Investment corpus",
                          "amount": round(remaining),
                          "split": {
                              "equity_MF": eq_amt,
                              "debt_MF_or_FD": debt_amt
                          },
                          "note": f"Equity {eq:.0%} / Debt {1-eq:.0%} per your risk profile"})

        return {
            "bonus_amount": round(amount),
            "deployment_plan": alloc,
            "tax_on_bonus": (
                f"Bonus is taxed as salary at your marginal rate "
                f"(~{_marginal_rate(annual_income):.0%}). "
                f"Estimated tax on bonus: ₹{amount * _marginal_rate(annual_income):,.0f}"
            ),
        }

    def _handle_marriage(self, amount, risk, annual_income, expenses, age, salary, data):
        partner_income_note = (
            "For optimal HRA claims, ensure rent agreement is in the name of the lower-income partner "
            "if they are in a lower tax bracket."
        )
        return {
            "joint_planning": {
                "hra_optimisation": partner_income_note,
                "nps_matching": (
                    "Both partners can claim NPS 80CCD(1B) deduction of ₹50,000 each "
                    "= ₹1,00,000 combined additional saving."
                ),
                "joint_insurance": (
                    "Consider a family floater health plan (₹10L+ cover) — "
                    "often cheaper than two individual policies."
                ),
                "combined_emergency_fund": (
                    f"Combined emergency fund target: "
                    f"₹{expenses * 9:,.0f} (9 months for two incomes)."
                ),
                "sip_split_advice": (
                    "Split SIPs across both PAN accounts to maximise LTCG tax exemption "
                    "(₹1.25L per person per year)."
                ),
            },
            "wedding_corpus_advice": (
                f"If wedding is planned: keep ₹{round(amount * 0.5):,.0f} liquid "
                f"and invest ₹{round(amount * 0.5):,.0f} in short-term debt fund "
                "if the wedding is >1 year away."
                if amount > 0 else
                "Specify wedding budget in life_event_amount for detailed advice."
            ),
        }

    def _handle_baby(self, amount, risk, annual_income, expenses, age, salary, data):
        # Education corpus planning (18 years away)
        current_education_cost = 2_500_000  # ₹25L at today's cost for engineering/MBA
        education_corpus_needed = current_education_cost * ((1.07) ** 18)  # 7% inflation
        months_to_education = 18 * 12
        monthly_return = (1.12) ** (1 / 12) - 1
        edu_sip = education_corpus_needed * monthly_return / (
            ((1 + monthly_return) ** months_to_education) - 1
        )

        return {
            "education_corpus": {
                "target_corpus_in_18_years": round(education_corpus_needed),
                "monthly_sip_required": round(edu_sip),
                "suggested_instrument": "Sukanya Samriddhi (girl child) or Child equity MF plan",
                "start_now": "Even ₹2,000/month started now becomes significantly more than ₹5,000 started in 5 years.",
            },
            "insurance_upgrade": {
                "life_cover": f"Increase term cover to ₹{round(annual_income * 15):,.0f} (15× income with dependent child).",
                "critical_illness": "Add critical illness rider or separate policy — ₹25L minimum.",
            },
            "emergency_fund_upgrade": (
                f"Increase emergency fund to 9 months: ₹{expenses * 9:,.0f} "
                "— childcare costs can be unpredictable."
            ),
            "maternity_paternity_tax": (
                "Childcare expenses can be claimed under LTA and medical reimbursement "
                "where applicable — consult CA."
            ),
        }

    def _handle_inheritance(self, amount, risk, annual_income, expenses, age, salary, data):
        # Inheritance is generally not taxable in India (no estate/inheritance tax)
        # However, income generated from inherited assets IS taxable
        eq = {"conservative": 0.30, "moderate": 0.55, "aggressive": 0.75}.get(risk, 0.55)
        debt_pct = 1 - eq

        return {
            "inheritance_amount": round(amount),
            "tax_on_inheritance": (
                "India has no inheritance tax. However, any income (dividends, rent, capital gains) "
                "from inherited assets will be taxable in your hands."
            ),
            "deployment_strategy": {
                "immediate_step": (
                    f"Park ₹{round(min(amount, expenses * 6)):,.0f} in liquid MF "
                    "while you plan deployment (don't rush into markets)."
                ),
                "3_month_plan": {
                    "equity_MF": round(amount * eq),
                    "debt_MF_or_bonds": round(amount * debt_pct * 0.5),
                    "emergency_top_up": round(amount * debt_pct * 0.3),
                    "direct_equity_if_experienced": round(amount * debt_pct * 0.2),
                },
                "note": f"Allocation based on '{risk}' risk profile."
            },
            "staggered_entry": (
                "Consider Systematic Transfer Plan (STP) from liquid to equity MF over 12 months "
                "to average out market entry price."
            ),
        }


def _marginal_rate(annual_income: float) -> float:
    if annual_income > 1_000_000:
        return 0.30
    elif annual_income > 500_000:
        return 0.20
    else:
        return 0.05
