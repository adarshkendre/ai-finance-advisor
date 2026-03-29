"""
AI Money Mentor — Flask API + Frontend
=======================================
Track 9: ET AI Hackathon 2026

Routes:
  GET  /                 — Frontend dashboard (HTML)
  POST /analyze          — Full financial analysis
  POST /update-plan      — Dynamic plan update (single field)
  GET  /health           — Service health check
  GET  /scenarios        — Preloaded demo scenarios
  GET  /api/info         — API service info (JSON)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from orchestrator.orchestrator import Orchestrator

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)
orchestrator = Orchestrator()


# ── Frontend ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── API Info ──────────────────────────────────────────────────────────────────

@app.route("/api/info")
def api_info():
    return jsonify({
        "service": "AI Money Mentor",
        "track": "Track 9 — ET AI Hackathon 2026",
        "version": "1.0.0",
        "agents": 7,
        "endpoints": ["/analyze", "/update-plan", "/scenarios", "/health"]
    })


# ── Health ────────────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({"status": "ok", "agents": 7})


# ── Analyze ───────────────────────────────────────────────────────────────────

@app.route("/analyze", methods=["POST"])
def analyze():
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
            "recovery": "Check input format and retry."
        }), 500
    except Exception as e:
        return jsonify({"error": "Unexpected error", "detail": str(e)}), 500


# ── Update Plan ───────────────────────────────────────────────────────────────

@app.route("/update-plan", methods=["POST"])
def update_plan():
    try:
        body = request.get_json(force=True)
        base = body.get("base_profile", {})
        change = body.get("change", {})

        if not base or not change:
            return jsonify({"error": "Provide 'base_profile' and 'change' fields."}), 400

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


# ── Scenarios ─────────────────────────────────────────────────────────────────

@app.route("/scenarios", methods=["GET"])
def scenarios():
    return jsonify({
        "scenario_1_fire_plan": {
            "label": "FIRE Plan",
            "description": "34-yr engineer, ₹24L/year, retire at 50 with ₹1.5L/month",
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
            "label": "Tax Optimisation",
            "description": "₹18L base, ₹3.6L HRA, multiple deductions — old vs new regime",
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
            "label": "New Baby",
            "description": "Insurance upgrade, education corpus & protection planning",
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
            "label": "Bonus Deployment",
            "description": "₹5L annual bonus — optimal investment strategy",
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
    print("  Frontend: http://0.0.0.0:5000/")
    print("  API:      http://0.0.0.0:5000/analyze")
    print("  Agents:   Orchestrator + 6 specialists")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
