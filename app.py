# ==========================================================
# 🎯 LOWEST PAYOUT 7-NUMBER LOTTERY FINDER
# Deterministic + Multiprocessing + Match Breakdown
# Numbers: 1–37 | Ticket size: 7 | No repeats
# ==========================================================

import streamlit as st
import pandas as pd
import time
from itertools import combinations
from multiprocessing import Pool, cpu_count

# ----------------------------
# STREAMLIT UI
# ----------------------------
st.set_page_config(page_title="Lowest Payout Lottery Finder", layout="wide")
st.title("🎯 Lowest Payout 7-Number Combination Finder")

uploaded_file = st.file_uploader(
    "📂 Upload Excel file (tickets in Column A)", type=["xlsx"]
)

TOP_RESULTS = st.selectbox("How many best combinations?", [10, 20, 50, 100], index=0)
MAX_COMBOS = st.number_input(
    "How many combinations to scan (deterministic)",
    min_value=10_000,
    max_value=500_000,
    value=100_000,
    step=10_000,
)

# ----------------------------
# PAYOUT RULES
# ----------------------------
PAYOUTS = {
    3: 15,
    4: 1000,
    5: 4000,
    6: 10000,
    7: 100000,
}

NUMBERS = list(range(1, 38))
COMBO_SIZE = 7

# ----------------------------
# HELPERS
# ----------------------------
def parse_tickets(df):
    tickets = []
    for val in df.iloc[:, 0]:
        nums = set(map(int, str(val).split(",")))
        if len(nums) == 7:
            tickets.append(nums)
    return tickets


def evaluate_combo(args):
    combo, tickets = args
    payout = 0
    breakdown = {3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

    for t in tickets:
        match = len(combo & t)
        if match >= 3:
            payout += PAYOUTS[match]
            breakdown[match] += 1

    return payout, tuple(sorted(combo)), breakdown


# ----------------------------
# MAIN LOGIC
# ----------------------------
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    tickets = parse_tickets(df)

    st.success(f"Loaded {len(tickets)} tickets")
    st.info("Running deterministic search with multiprocessing")

    start_time = time.time()

    # Generate deterministic combinations (first N)
    selected_combos = []
    for i, c in enumerate(combinations(NUMBERS, COMBO_SIZE)):
        if i >= MAX_COMBOS:
            break
        selected_combos.append(set(c))

    # Multiprocessing
    with Pool(cpu_count()) as pool:
        results = pool.map(
            evaluate_combo, [(c, tickets) for c in selected_combos]
        )

    # Sort and select best
    results.sort(key=lambda x: x[0])
    best = results[:TOP_RESULTS]

    # ----------------------------
    # RESULTS TABLE
    # ----------------------------
    rows = []
    for idx, (payout, combo, breakdown) in enumerate(best, start=1):
        rows.append(
            {
                "Rank": idx,
                "Combination": ",".join(map(str, combo)),
                "Total Payout (₹)": payout,
                "3-Match Tickets": breakdown[3],
                "4-Match Tickets": breakdown[4],
                "5-Match Tickets": breakdown[5],
                "6-Match Tickets": breakdown[6],
                "7-Match Tickets": breakdown[7],
            }
        )

    result_df = pd.DataFrame(rows)

    st.subheader(f"🏆 Top {TOP_RESULTS} Lowest Payout Combinations")
    st.dataframe(result_df, use_container_width=True)

    # ----------------------------
    # DOWNLOAD
    # ----------------------------
    

    st.success(
        f"Completed in {time.time() - start_time:.2f} seconds using {cpu_count()} CPU cores"
    )
