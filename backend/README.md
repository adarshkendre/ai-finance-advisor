# 📘 AI Financial Advisor – Backend

---

# 🧠 Overview

This project is a Flask-based backend system for an AI-powered Financial Advisor. It analyzes user financial data and provides:

* 📊 Financial Health Score
* 📈 FIRE (Financial Independence, Retire Early) Planning
* 💰 Tax Optimization (Old vs New Regime)
* 🤖 Personalized Financial Advice

The system follows a **multi-agent (service-based) architecture**, making it modular, scalable, and easy to maintain.

---

# 🚀 Features

✅ Input validation and error handling
✅ Financial health analysis (Savings, Expenses, Debt)
✅ Multi-scenario user classification
✅ Retirement planning (FIRE model)
✅ Tax regime comparison
✅ AI-based rule-driven advice system
✅ Step-by-step explainable calculations
✅ REST API for frontend integration

---

# 🧠 Architecture

User Input (JSON / UI)
↓
Flask API (/analyze)
↓
Data Agent (Validation)
↓
Scenario Agent (User Classification)
↓
Analysis Agent (Health Score)
↓
Planning Agent (FIRE)
↓
Tax Agent (Optimization)
↓
AI Advisor Agent (Advice)
↓
Final JSON Response

---

# 📁 Folder Structure

```
backend/

│
├── app.py                      # Main Flask application
│
├── services/
│   ├── data_agent.py           # Input validation & cleaning
│   ├── scenario_agent.py       # Scenario classification
│   ├── analysis_agent.py       # Financial scoring logic
│   ├── planning_agent.py       # FIRE calculations
│   ├── tax_agent.py            # Tax comparison
│   └── ai_agent.py             # Advice generation
│
├── utils/
│   ├── helpers.py              # Financial calculations
│   └── validator.py            # Input validation logic
│
├── test_api.py                 # API testing script
├── requirements.txt            # Dependencies
```

---

# ⚙️ Installation & Setup

### 1️⃣ Download the code 

```bash
cd backend
```

### 2️⃣ Install dependencies

```bash
pip install flask requests
```

### 3️⃣ Run the server

```bash
python app.py
```

Server will start at:

```
http://127.0.0.1:5000
```

---

# 🌐 API Documentation

## 🔥 Endpoint

POST `/analyze`

---

## 📥 Request Body

```json
{
  "income": 50000,
  "expenses": 30000,
  "savings": 10000,
  "debt": 5000,
  "age": 25
}
```

---

## 📤 Response

```json
{
  "message": "Analysis complete",
  "scenario": "High Income User",
  "data": {
    "income": 50000,
    "expenses": 30000,
    "savings": 10000,
    "debt": 5000,
    "age": 25
  },
  "analysis": {
    "score": 100,
    "status": "Good",
    "confidence": "High",
    "calculation": {
      "savings_rate": 20.0,
      "expense_ratio": 60.0,
      "debt_ratio": 0.1
    },
    "step_by_step": {
      "savings_rate_calc": "10000 / 50000 = 0.2",
      "expense_ratio_calc": "30000 / 50000 = 0.6",
      "debt_ratio_calc": "5000 / 50000 = 0.1"
    }
  },
  "planning": {
    "fire_target": 9000000,
    "sip_required": 21404.76,
    "years_left": 35
  },
  "tax": {
    "recommended": "Old Regime",
    "tax_savings": 5000
  },
  "advice": [
    "Your savings rate is healthy. Keep it up!",
    "To reach your FIRE goal, increase your monthly investment.",
    "Old Regime is better for you."
  ],
  "priorities": [],
  "disclaimer": "This is AI-generated guidance and not licensed financial advice."
}
```

---

# ❌ Error Handling

### Example:

```json
{
  "error": "Income must be greater than 0"
}
```

### Rules:

* All fields are required
* Income must be greater than 0
* Prevents division by zero
* Ensures valid numeric inputs

---

# 🧪 Testing

### Run test script:

```bash
python test_api.py
```

### Or use Postman:

* Method: POST
* URL: http://127.0.0.1:5000/analyze
* Body: JSON

---

# 📊 Core Logic & Formulas

## 🔹 Financial Health

Savings Rate = savings / income
Expense Ratio = expenses / income
Debt Ratio = debt / income

---

## 🔹 FIRE Calculation

FIRE Target = expenses × 12 × 25
Years Left = 60 - age
SIP Required = FIRE Target / (years × 12)

---

## 🔹 Tax Optimization

* Compare Old vs New regime
* Recommend lower tax option

---

## 🔹 AI Advice

Rule-based suggestions based on:

* Savings rate
* Expense ratio
* Debt ratio
* Scenario classification
* Investment gap
* Tax savings

---

# 🎯 Frontend Integration Guide

### 1️⃣ Collect Inputs

* income
* expenses
* savings
* debt
* age

---

### 2️⃣ Send API Request

```javascript
fetch("http://127.0.0.1:5000/analyze", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(data)
})
.then(res => res.json())
.then(result => console.log(result));
```

---

### 3️⃣ Display Results

| Backend Field         | UI Display         |
| --------------------- | ------------------ |
| analysis.score        | Health Score       |
| planning.fire_target  | FIRE Goal          |
| planning.sip_required | Monthly Investment |
| advice                | Suggestions        |
| tax.recommended       | Best Tax Option    |

---

# 🏆 Key Highlights

* Modular multi-agent design
* Explainable financial logic
* Scenario-based intelligence
* Real-world problem solving
* Clean and scalable API

---

# 🚀 Future Improvements

* Real-world tax slabs (India)
* Machine learning integration
* Investment portfolio suggestions
* Dashboard with charts

---

# 🏁 Conclusion

This backend serves as the **core intelligence layer** of the AI Financial Advisor, transforming raw financial data into meaningful insights, financial planning, and actionable advice.
