def generate_advice(analysis, planning, tax):
    advice = []
    priorities = []

    scenario = analysis.get("scenario", "")
    savings_rate = analysis["calculation"]["savings_rate"]

    # General advice
    if savings_rate > 30:
        advice.append("Excellent savings rate! You're financially disciplined.")
    else:
        advice.append("Try to increase your savings rate.")

    # Scenario-based advice
    if scenario == "High Income User":
        advice.append("You earn well. Focus on wealth creation through investments.")

    elif scenario == "High Debt User":
        advice.append("Your debt is high. Prioritize clearing it first.")
        priorities.append("Debt repayment (Critical)")

    elif scenario == "Low Savings User":
        advice.append("Start building an emergency fund.")
        priorities.append("Increase savings (High Priority)")

    elif scenario == "Young Beginner":
        advice.append("Start investing early to benefit from compounding.")

    # FIRE
    if planning["years_left"] > 0:
        advice.append("You are on track to achieve your FIRE goal.")

    # Tax
    advice.append(f"{tax['recommended']} is better. You save ₹{tax['tax_savings']}.")

    return {
        "advice": advice,
        "priorities": priorities
    }