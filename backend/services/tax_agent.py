def calculate_tax(data):
    income = data["income"]
    deductions = 150000

    taxable_old = max(income - deductions, 0)
    tax_old = taxable_old * 0.2

    taxable_new = income
    tax_new = taxable_new * 0.3

    recommended = "Old Regime" if tax_old < tax_new else "New Regime"

    return {
        "recommended": recommended,
        "tax_savings": abs(tax_new - tax_old),
        "tax_breakdown": {
            "old_regime": {
                "income": income,
                "deductions": deductions,
                "taxable_income": taxable_old,
                "tax": tax_old,
                "calculation": f"({income} - {deductions}) × 20% = {tax_old}"
            },
            "new_regime": {
                "income": income,
                "taxable_income": taxable_new,
                "tax": tax_new,
                "calculation": f"{income} × 30% = {tax_new}"
            }
        }
    }