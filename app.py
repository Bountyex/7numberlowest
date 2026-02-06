# ==========================================
# LOTTERY LOWEST PAYOUT FINDER (Streamlit)
# ==========================================

import streamlit as st
import pandas as pd
import itertools
from collections import Counter

st.title("🎯 Lottery Lowest Payout Finder")

st.write("Upload Excel file (Column A = tickets like 1,2,3,4,5,6,7)")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    tickets = df.iloc[:, 0].dropna().apply(
        lambda x: set(map(int, str(x).split(",")))
    ).tolist()

    st.success(f"Total Tickets Loaded: {len(tickets)}")

    payout_rules = {
        3: 15,
        4: 1000,
        5: 4000,
        6: 10000,
        7: 100000
    }

    def calculate_payout(comb_set):
        total = 0
        for ticket in tickets:
            match = len(comb_set & ticket)
            if match >= 3:
                total += payout_rules.get(match, 0)
        return total

    LEAST_NUMBERS_TO_USE = st.slider(
        "Select search depth (higher = slower but deeper)",
        min_value=15,
        max_value=25,
        value=18
    )

    if st.button("🔍 Find Lowest Payout"):

        with st.spinner("Calculating frequencies..."):

            freq = Counter()
            for ticket in tickets:
                for num in ticket:
                    freq[num] += 1

            least_numbers = [
                num for num, _ in sorted(freq.items(), key=lambda x: x[1])[:LEAST_NUMBERS_TO_USE]
            ]

            results = []

            for comb in itertools.combinations(least_numbers, 7):
                payout = calculate_payout(set(comb))
                results.append((comb, payout))

            results_sorted = sorted(results, key=lambda x: x[1])

        st.subheader("🏆 Top 10 Lowest Payout Results")

        for i in range(min(10, len(results_sorted))):
            combo, payout = results_sorted[i]
            st.write(f"{i+1}. {combo} → ₹{payout}")

        st.success(f"✅ Lowest Payout Found: {results_sorted[0]}")
