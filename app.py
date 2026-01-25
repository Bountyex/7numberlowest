# ==========================================================
# 🎯 LOWEST PAYOUT 7-NUMBER LOTTERY FINDER
# Numbers: 1–37 | Ticket size: 7 | No repeats
# Streamlit Cloud SAFE version
# ==========================================================

import streamlit as st
import pandas as pd
import random
import time
import io

# ----------------------------
# STREAMLIT UI
# ----------------------------
st.set_page_config(page_title="Lowest Payout Lottery Finder", layout="wide")
st.title("🎯 Lowest Payout 7-Number Combination Finder")

uploaded_file = st.file_uploader(
    "📂 Upload Excel file (tickets in Column A)",
    type=["xlsx"]
)

TOP_RESULTS = st.selectbox("How many results?", [10, 20, 50, 100], index=0)

# ----------------------------
# PAYOUT RULES
# ----------------------------
PAYOUTS = {
    3: 15,
    4: 1000,
    5: 4000,
    6: 10000,
    7: 100000
}

NUMBERS = list(range(1, 38))
COMBO_SIZE = 7
MAX_ITERATIONS = 100_000   # SAFE for Streamlit Cloud
TIME_LIMIT = 120           # seconds

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


def calculate_payout(combo, tickets):
    total = 0
    match_count = {3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

    for t in tickets:
        match = len(combo & t)
        if match >= 3:
            total += PAYOUTS[match]
            match_count[match] += 1

    return total, match_count


# ----------------------------
# MAIN LOGIC
# ----------------------------
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    tickets = parse_tickets(df)

    st.success(f"Loaded {len(tickets)} tickets")

    start_time = time.time()
    best_results = []

    progress = st.progress(0)
    status = st.empty()

    for i in range(MAX_ITERATIONS):
        if time.time() - start_time > TIME_LIMIT:
            break

        combo = set(random.sample(NUMBERS, COMBO_SIZE))
        payout, breakdown = calculate_payout(combo, tickets)

        best_results.append(
            (
                payout,
                tuple(sorted(combo)),
                breakdown
            )
        )

        # Keep only best N
        best_results = list(set(best_results))
        best_results.sort(key=lambda x: x[0])
        best_results = best_results[:TOP_RESULTS]

        if i % 5000 == 0:
            progress.progress(min(i / MAX_ITERATIONS, 1.0))
            status.text(f"Checked {i:,} combinations")

    progress.progress(1.0)

    # ----------------------------
    # RESULTS TABLE
    # ----------------------------
    rows = []
    for idx, (payout, combo, breakdown) in enumerate(best_results, start=1):
        rows.append({
            "Rank": idx,
            "Combination": ",".join(map(str, combo)),
            "Total Payout (₹)": payout,
            "3-Match Tickets": breakdown[3],
            "4-Match Tickets": breakdown[4],
            "5-Match Tickets": breakdown[5],
            "6-Match Tickets": breakdown[6],
            "7-Match Tickets": breakdown[7],
        })

    result_df = pd.DataFrame(rows)

    st.subheader(f"🏆 Top {TOP_RESULTS} Lowest Payout Combinations")
    st.dataframe(result_df, use_container_width=True)

    # ----------------------------
    # DOWNLOAD (FIXED)
    # ----------------------------
    buffer = io.BytesIO()
    result_df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    st.download_button(
        label="⬇️ Download Results as Excel",
        data=buffer,
        file_name="lowest_payout_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.success(f"Completed in {time.time() - start_time:.2f} seconds")
