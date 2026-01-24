import pandas as pd
import random
from itertools import combinations

# ==============================
# CONFIG
# ==============================
EXCEL_FILE = "tickets.xlsx"   # change if needed
ITERATIONS = 100_000          # increase for better results

PAYOUT = {
    3: 15,
    4: 1000,
    5: 4000,
    6: 10000,
    7: 100000
}

NUMBERS = list(range(1, 38))


# ==============================
# LOAD TICKETS
# ==============================
def load_tickets(path):
    df = pd.read_excel(path)
    tickets = []
    for v in df.iloc[:, 0]:
        ticket = set(int(x) for x in str(v).split(","))
        tickets.append(ticket)
    return tickets


# ==============================
# PAYOUT CALCULATION
# ==============================
def total_payout(result, tickets):
    total = 0
    for t in tickets:
        match = len(result & t)
        if match >= 3:
            total += PAYOUT[match]
    return total


# ==============================
# SEARCH LOWEST PAYOUT
# ==============================
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
# MAIN
# ==============================
if __name__ == "__main__":
    tickets = load_tickets(EXCEL_FILE)
    results = find_best_combinations(tickets, ITERATIONS)

    print("\n🎯 TOP 10 LOWEST PAYOUT COMBINATIONS\n")
    for i, (pay, combo) in enumerate(results, 1):
        print(f"{i}. {combo}  →  ₹{pay}")
