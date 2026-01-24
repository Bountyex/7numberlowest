from flask import Flask, request, jsonify
import pandas as pd
import random
import os

# ==============================
# APP SETUP
# ==============================
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ==============================
# CONFIG
# ==============================
ITERATIONS = 100_000

PAYOUT = {
    3: 15,
    4: 1000,
    5: 4000,
    6: 10000,
    7: 100000
}

NUMBERS = list(range(1, 38))

# ==============================
# HELPERS
# ==============================
def load_tickets(file_path):
    df = pd.read_excel(file_path)
    tickets = []
    for v in df.iloc[:, 0]:
        ticket = set(int(x) for x in str(v).split(","))
        tickets.append(ticket)
    return tickets


def total_payout(result, tickets):
    total = 0
    for t in tickets:
        match = len(result & t)
        if match >= 3:
            total += PAYOUT[match]
    return total


def find_best_combinations(tickets, iterations):
    seen = set()
    best = []

    for _ in range(iterations):
        combo = tuple(sorted(random.sample(NUMBERS, 7)))
        if combo in seen:
            continue
        seen.add(combo)

        payout = total_payout(set(combo), tickets)
        best.append((payout, combo))

    best.sort(key=lambda x: x[0])
    return best[:10]

# ==============================
# ROUTES
# ==============================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Upload an Excel file using POST /upload",
        "format": "Column A: 7 numbers separated by commas"
    })


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(path)

    tickets = load_tickets(path)
    results = find_best_combinations(tickets, ITERATIONS)

    output = []
    for rank, (pay, combo) in enumerate(results, 1):
        output.append({
            "rank": rank,
            "combination": combo,
            "total_payout": pay
        })

    return jsonify({
        "total_tickets": len(tickets),
        "top_10_results": output
    })


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
