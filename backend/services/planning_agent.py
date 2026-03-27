def calculate_fire(data):
    age = data["age"]
    expenses = data["expenses"]

    annual_expenses = expenses * 12
    fire_target = annual_expenses * 25
    years_left = 60 - age

    sip = fire_target / (years_left * 12) if years_left > 0 else 0

    return {
        "fire_target": fire_target,
        "years_left": years_left,
        "sip_required": round(sip, 2),
        "formula_used": {
            "fire_target": "Annual Expenses × 25",
            "sip": "Target / (Years × 12)"
        },
        "step_by_step": {
            "annual_expenses": f"{expenses} × 12 = {annual_expenses}",
            "fire_target_calc": f"{annual_expenses} × 25 = {fire_target}",
            "years_left_calc": f"60 - {age} = {years_left}",
            "sip_calc": f"{fire_target} / ({years_left} × 12) = {round(sip, 2)}"
        }
    }