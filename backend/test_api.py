import requests

url = "http://127.0.0.1:5000/analyze"

test_cases = [
    {"income": 200000, "expenses": 80000, "savings": 70000, "debt": 10000, "age": 30},
    {"income": 50000, "expenses": 30000, "savings": 5000, "debt": 40000, "age": 28},
    {"income": 60000, "expenses": 55000, "savings": 1000, "debt": 2000, "age": 26},
    {"income": 30000, "expenses": 15000, "savings": 5000, "debt": 0, "age": 22}
]

for case in test_cases:
    print("\nINPUT:", case)

    try:
        response = requests.post(url, json=case)

        print("STATUS CODE:", response.status_code)

        # 🔥 Safe JSON handling
        try:
            print("OUTPUT:", response.json())
        except:
            print("RAW RESPONSE:", response.text)

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Flask server is not running!")