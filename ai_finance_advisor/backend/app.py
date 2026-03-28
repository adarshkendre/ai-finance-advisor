"""
AI Money Mentor — Flask API
============================
Track 9: ET AI Hackathon 2026

Routes:
  POST /analyze          — Full financial analysis (main flow)
  POST /update-plan      — Dynamic plan update (change one input)
  GET  /health           — Service health check
  GET  /scenarios        — Return preloaded demo scenarios

Every route returns a full audit_trail for judge review.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify
from flask_cors import CORS
from orchestrator.orchestrator import Orchestrator

app = Flask(__name__)
CORS(app)
orchestrator = Orchestrator()


@app.route("/")
def home():
    return jsonify({
        "service": "AI Money Mentor",
        "track": "Track 9 — ET AI Hackathon 2026",
        "version": "1.0.0",
        "endpoints": ["/analyze", "/update-plan", "/scenarios", "/health"]
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok", "agents": 7})


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Main analysis endpoint.
    Accepts full user financial profile and returns a complete plan.
    """
    try:
        user_input = request.get_json(force=True)
        if not user_input:
            return jsonify({"error": "Request body must be JSON"}), 400

        result = orchestrator.run(user_input)

        status_code = 200 if result.get("status") == "success" else 400
        return jsonify(result), status_code

    except RuntimeError as e:
        return jsonify({
            "error": "Agent pipeline failure",
            "detail": str(e),
            "recovery": "Check input format and retry. If issue persists, contact support."
        }), 500
    except Exception as e:
        return jsonify({
            "error": "Unexpected error",
            "detail": str(e)
        }), 500


@app.route("/update-plan", methods=["POST"])
def update_plan():
    """
    Dynamic plan update — user changes ONE field (e.g. retirement age from 50 to 55).
    Re-runs the full pipeline with the updated field merged into the base profile.

    Body: { "base_profile": {...}, "change": {"field": "target_retirement_age", "value": 55} }
    """
    try:
        body = request.get_json(force=True)
        base = body.get("base_profile", {})
        change = body.get("change", {})

        if not base or not change:
            return jsonify({
                "error": "Provide 'base_profile' and 'change' fields.",
                "example": {
                    "base_profile": {"age": 34, "monthly_income": 200000},
                    "change": {"field": "target_retirement_age", "value": 55}
                }
            }), 400

        # Merge the change
        field = change.get("field")
        value = change.get("value")
        if not field:
            return jsonify({"error": "change.field is required"}), 400

        updated_profile = {**base, field: value}
        result = orchestrator.run(updated_profile)
        result["change_applied"] = {field: value}

        return jsonify(result), 200 if result.get("status") == "success" else 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/scenarios", methods=["GET"])
def scenarios():
    """
    Returns pre-built demo scenarios for hackathon judges.
    These match the mandatory Track 9 scenario pack exactly.
    """
    return jsonify({
        "scenario_1_fire_plan": {
            "description": (
                "Track 9 mandatory — 34-year-old software engineer, "
                "₹24L/year, ₹18L MF, ₹6L PPF, retire at 50 with ₹1.5L/month"
            ),
            "input": {
                "age": 34,
                "monthly_income": 200000,
                "monthly_expenses": 80000,
                "existing_investments": 1800000,
                "salary_structure": {"ppf_balance": 600000},
                "target_retirement_age": 50,
                "target_monthly_corpus": 150000,
                "risk_profile": "moderate",
            }
        },
        "scenario_2_tax_edge_case": {
            "description": (
                "Track 9 mandatory — ₹18L base, ₹3.6L HRA, ₹1.5L 80C, "
                "₹50K NPS, ₹40K home loan interest"
            ),
            "input": {
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
            }
        },
        "scenario_3_life_event_baby": {
            "description": "New baby — insurance upgrade, education corpus planning",
            "input": {
                "age": 30,
                "monthly_income": 120000,
                "monthly_expenses": 50000,
                "existing_investments": 500000,
                "life_event": "baby",
                "life_event_amount": 0,
                "risk_profile": "moderate",
            }
        },
        "scenario_4_bonus_deployment": {
            "description": "Annual bonus of ₹5L — optimal deployment strategy",
            "input": {
                "age": 28,
                "monthly_income": 100000,
                "monthly_expenses": 40000,
                "existing_investments": 300000,
                "life_event": "bonus",
                "life_event_amount": 500000,
                "salary_structure": {"deductions_80c": 50000},
                "risk_profile": "aggressive",
            }
        }
    })


if __name__ == "__main__":
    print("=" * 60)
    print("  AI Money Mentor — Track 9 ET AI Hackathon 2026")
    print("  Running at http://127.0.0.1:5000")
    print("  Agents: Orchestrator + 6 specialists")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
