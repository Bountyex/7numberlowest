import streamlit as st
import pandas as pd
import random
import heapq

st.set_page_config(page_title="Lottery Payout Minimizer", layout="wide")

st.title("🎯 Lottery Lowest Payout Finder")
st.write("Upload your Excel file containing 7-number lottery tickets (1–37).")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

# Payout structure
PAYOUTS = {
    3: 15,
    4: 1000,
    5: 4000,
    6: 10000,
    7: 100000
}

def calculate_payout(combo_set, tickets):
    total = 0
    for ticket in tickets:
        matches = len(combo_set & ticket)
        if matches >= 3:
            total += PAYOUTS.get(matches, 0)
    return total

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    tickets = []
    for ticket in df.iloc[:, 0].dropna():
        nums = set(map(int, str(ticket).split(',')))
        tickets.append(nums)

    st.success(f"Loaded {len(tickets)} tickets.")

    iterations = st.slider("Search Depth (Higher = Better Results)", 
                           min_value=50000, 
                           max_value=500000, 
                           value=150000, 
                           step=50000)

    if st.button("Find Lowest Payout Combinations"):

        numbers = list(range(1, 38))
        top_heap = []
        seen = set()

        with st.spinner("Searching... Please wait..."):

            for _ in range(iterations):
                combo = tuple(sorted(random.sample(numbers, 7)))

                if combo in seen:
                    continue
                seen.add(combo)

                payout = calculate_payout(set(combo), tickets)

                if len(top_heap) < 10:
                    heapq.heappush(top_heap, (-payout, combo))
                else:
                    if payout < -top_heap[0][0]:
                        heapq.heappushpop(top_heap, (-payout, combo))

        results = sorted([(-p, c) for p, c in top_heap], key=lambda x: x[0])

        st.subheader("🏆 Top 10 Lowest Payout Combinations")

        for payout, combo in results:
            st.write(f"Combination: {combo} → Total Payout: ₹{payout:,}")
