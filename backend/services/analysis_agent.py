def analyze_financials(data):
    income = data["income"]
    expenses = data["expenses"]
    savings = data["savings"]
    debt = data["debt"]
    age = data["age"]

    savings_rate = savings / income
    expense_ratio = expenses / income
    debt_ratio = debt / income

    score = 100

    if savings_rate < 0.2:
        score -= 20
    if expense_ratio > 0.6:
        score -= 20
    if debt_ratio > 0.5:
        score -= 30

    # Scenario detection
    if age < 25:
        scenario = "Young Beginner"
    elif income > 150000:
        scenario = "High Income User"
    elif debt_ratio > 0.5:
        scenario = "High Debt User"
    elif savings_rate < 0.2:
        scenario = "Low Savings User"
    else:
        scenario = "Balanced User"

    return {
        "score": score,
        "status": "Good" if score >= 70 else "Needs Improvement",
        "confidence": "High",
        "scenario": scenario,
        "calculation": {
            "savings_rate": savings_rate * 100,
            "expense_ratio": expense_ratio * 100,
            "debt_ratio": debt_ratio
        },
        "step_by_step": {
            "savings_rate_calc": f"{savings} / {income} = {round(savings_rate, 2)}",
            "expense_ratio_calc": f"{expenses} / {income} = {round(expense_ratio, 2)}",
            "debt_ratio_calc": f"{debt} / {income} = {round(debt_ratio, 2)}",
            "initial_score": 100,
            "final_score": score
        }
    }