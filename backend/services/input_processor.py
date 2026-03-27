def process_user_data(data):
    income = float(data.get("income", 0))
    expenses = float(data.get("expenses", 0))
    savings = float(data.get("savings", 0))
    debt = float(data.get("debt", 0))
    age = int(data.get("age", 25))

    if income <= 0:
        raise ValueError("Income must be greater than 0")

    return {
        "income": income,
        "expenses": expenses,
        "savings": savings,
        "debt": debt,
        "age": age
    }