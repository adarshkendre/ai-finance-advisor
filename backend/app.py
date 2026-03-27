from flask import Flask, request, jsonify
from services.input_processor import process_user_data
from services.analysis_agent import analyze_financials
from services.planning_agent import calculate_fire
from services.tax_agent import calculate_tax
from services.advice_agent import generate_advice

app = Flask(__name__)

# ✅ Home route
@app.route("/")
def home():
    return "AI Financial Advisor Backend Running!"

# ✅ MAIN API ROUTE (VERY IMPORTANT)
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        user_input = request.json

        data = process_user_data(user_input)
        analysis = analyze_financials(data)
        planning = calculate_fire(data)
        tax = calculate_tax(data)
        advice_data = generate_advice(analysis, planning, tax)

        return jsonify({
            "message": "Analysis complete",
            "scenario": analysis["scenario"],
            "data": data,
            "analysis": analysis,
            "planning": planning,
            "tax": tax,
            "advice": advice_data["advice"],
            "priorities": advice_data["priorities"],
            "disclaimer": "This is AI-generated guidance and not licensed financial advice."
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)