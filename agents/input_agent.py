"""
Input Agent
-----------
Validates and normalises raw user input.
Detects missing or invalid fields and returns them so the
Orchestrator can ask the user for clarification rather than crashing.
"""

REQUIRED_FIELDS = {
    "age": (1, 100, "Your current age in years (e.g. 34)"),
    "monthly_income": (0, 10_000_000, "Your gross monthly income in ₹"),
    "monthly_expenses": (0, 10_000_000, "Your total monthly expenses in ₹"),
    "existing_investments": (0, 1_000_000_000, "Total existing investments in ₹ (MF + PPF + stocks etc.)"),
}

OPTIONAL_FIELDS = {
    "monthly_savings": None,          # computed if missing
    "debt_emi": 0,
    "target_retirement_age": 60,
    "target_monthly_corpus": None,
    "risk_profile": "moderate",       # conservative | moderate | aggressive
    "life_event": None,               # bonus | marriage | baby | inheritance
    "life_event_amount": 0,
    "salary_structure": None,         # for tax wizard: dict of HRA, 80C, NPS etc.
    "tax_regime_preference": None,    # old | new | None (auto-detect best)
}

VALID_RISK_PROFILES = {"conservative", "moderate", "aggressive"}
VALID_LIFE_EVENTS = {"bonus", "marriage", "baby", "inheritance", None}


class InputAgent:
    def run(self, raw: dict) -> tuple:
        """
        Returns (validated_dict, missing_fields_list).
        missing_fields is empty when input is complete and valid.
        """
        errors = []
        out = {}

        # Validate required fields
        for field, (lo, hi, hint) in REQUIRED_FIELDS.items():
            val = raw.get(field)
            if val is None:
                errors.append({"field": field, "hint": hint})
                continue
            try:
                val = float(val)
            except (TypeError, ValueError):
                errors.append({"field": field, "hint": f"{hint} — must be a number"})
                continue
            if not (lo <= val <= hi):
                errors.append({
                    "field": field,
                    "hint": f"{hint} — must be between {lo} and {hi:,}"
                })
                continue
            out[field] = val

        if errors:
            return {}, errors

        # Age must be integer
        out["age"] = int(out["age"])

        # Logical cross-field checks
        if out["monthly_expenses"] > out["monthly_income"] * 1.5:
            errors.append({
                "field": "monthly_expenses",
                "hint": "Monthly expenses seem higher than income. Please double-check."
            })
        if errors:
            return {}, errors

        # Fill optional fields with defaults / derivations
        for field, default in OPTIONAL_FIELDS.items():
            raw_val = raw.get(field, default)
            out[field] = raw_val

        # Derive monthly_savings if not provided
        if out["monthly_savings"] is None:
            out["monthly_savings"] = max(
                0.0,
                out["monthly_income"] - out["monthly_expenses"] - out.get("debt_emi", 0)
            )
        else:
            out["monthly_savings"] = float(out["monthly_savings"])

        # Derive target_monthly_corpus from expenses if not given (4% rule)
        if out["target_monthly_corpus"] is None:
            out["target_monthly_corpus"] = out["monthly_expenses"]

        # Normalise risk profile
        if out["risk_profile"] not in VALID_RISK_PROFILES:
            out["risk_profile"] = "moderate"

        # Normalise life event
        life_event = out.get("life_event")
        if isinstance(life_event, str):
            life_event = life_event.lower().strip() or None
        if life_event not in VALID_LIFE_EVENTS:
            life_event = None
        out["life_event"] = life_event

        return out, []

    @staticmethod
    def clarification_message(missing_fields: list) -> str:
        lines = ["I need a few more details to build your financial plan:"]
        for mf in missing_fields:
            lines.append(f"  • {mf['field']}: {mf['hint']}")
        return "\n".join(lines)
