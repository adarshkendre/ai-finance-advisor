def validate_input(data):
    if data["income"] <= 0:
        return {"error": "Income must be greater than 0"}