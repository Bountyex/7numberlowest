# 🎯 Lottery Lowest Payout Finder

This Streamlit app finds the 7-number combination (1–37) that produces the lowest total payout
based on uploaded lottery tickets.

## How It Works
- Upload Excel file
- Column A must contain tickets like: 1,2,3,4,5,6,7
- App searches combinations using least frequent numbers
- Returns Top 10 lowest payout combinations

## Run Locally

pip install -r requirements.txt
streamlit run app.py
