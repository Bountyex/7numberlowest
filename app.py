import streamlit as st
import pandas as pd
import numpy as np
import random, math, heapq

# =========================================================
# APP CONFIG
# =========================================================
st.set_page_config(page_title="⚡ 7 Number Lowest Result (FAST)", layout="wide")
st.title("⚡ 7 Number Lowest Result — FAST ENGINE")

# =========================================================
# FILE UPLOAD
# =========================================================
uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])
if uploaded_file is None:
    st.stop()

# =========================================================
# READ + CLEAN COLUMNS
# =========================================================
df = pd.read_excel(uploaded_file)
df.columns = (
    df.columns.astype(str)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

# =========================================================
# AUTO-DETECT NUMBERS COLUMN
# =========================================================
possible_cols = [
    c for c in df.columns
    if ("selected" in c.lower())
    or ("number" in c.lower())
    or ("ticket" in c.lower())
]

if not possible_cols:
    st.error("❌ No column with ticket numbers found.")
    st.write("📌 Columns found:", df.columns.tolist())
    st.stop()

numbers_col = possible_cols[0]
st.success(f"✅ Using column: {numbers_col}")

# =========================================================
# PARSE TICKETS
# =========================================================
def parse_ticket(x):
    if pd.isna(x):
        return None
    try:
        s = str(x).replace(";", ",")
        nums = []
        for p in s.split(","):
            p = p.strip()
            if p.isdigit():
                nums.append(int(p))
            else:
                d = "".join(ch for ch in p if ch.isdigit())
                if d:
                    nums.append(int(d))
        nums = sorted(set(nums))
        if len(nums) == 7 and all(1 <= n <= 37 for n in nums):
            return tuple(nums)
    except:
        pass
    return None

tickets = df[numbers_col].dropna().apply(parse_ticket).dropna().tolist()
n = len(tickets)

if n == 0:
    st.error("❌ No valid 7-number tickets found.")
    st.stop()

st.success(f"🎟️ Loaded {n} valid tickets")

# =========================================================
# INDICATOR MATRIX (CACHED)
# =========================================================
@st.cache_data(show_spinner=False)
def build_indicator(tickets):
    M = np.zeros((len(tickets), 37), dtype=np.uint8)
    for i, t in enumerate(tickets):
        M[i, np.array(t) - 1] = 1
    return M

ind = build_indicator(tickets)

# =========================================================
# PAYOUT VECTOR
# =========================================================
payout = np.array([0, 0, 0, 15, 1000, 4000, 10000, 100000], dtype=np.int64)

# =========================================================
# SCORER
# =========================================================
def score_candidate(mask):
    counts = ind @ mask
    return payout[counts].sum()

# =========================================================
# FREQUENCY HEURISTIC
# =========================================================
freq = ind.sum(axis=0)
low_nums = np.argsort(freq)[:14]

# =========================================================
# NEIGHBOR
# =========================================================
def neighbor(mask):
    new = mask.copy()
    ones = np.flatnonzero(new)
    zeros = np.flatnonzero(new == 0)
    new[random.choice(ones)] = 0
    new[random.choice(zeros)] = 1
    return new

# =========================================================
# SIMULATED ANNEALING
# =========================================================
def fast_sa(mask, iters=1500, t0=5.0):
    best = curr = mask
    best_s = curr_s = score_candidate(curr)

    for i in range(iters):
        T = t0 * (1 - i / iters)
        cand = neighbor(curr)
        s = score_candidate(cand)
        d = s - curr_s

        if d < 0 or random.random() < math.exp(-d / (T + 1e-9)):
            curr, curr_s = cand, s
            if s < best_s:
                best, best_s = cand, s
    return best, best_s

# =========================================================
# INITIAL POPULATION
# =========================================================
def make_mask(nums):
    m = np.zeros(37, dtype=np.uint8)
    m[nums] = 1
    return m

candidates = []
for _ in range(30):
    candidates.append(make_mask(random.sample(list(low_nums), 7)))
for _ in range(40):
    candidates.append(make_mask(random.sample(range(37), 7)))
candidates.append(make_mask(low_nums[:7]))

# =========================================================
# RUN
# =========================================================
if st.button("🚀 Run Fast Optimization"):
    st.info("⏳ Optimizing…")

    bar = st.progress(0)
    heap = []
    counter = 0   # 🔑 tie-breaker

    for i, c in enumerate(candidates):
        b, s = fast_sa(c)
        heapq.heappush(heap, (s, counter, b))
        counter += 1
        heap = heapq.nsmallest(20, heap)
        bar.progress((i + 1) / len(candidates))

    # =====================================================
    # FINAL LOCAL REFINEMENT
    # =====================================================
    results = []

    for s, _, m in heap[:10]:
        best_m, best_s = m, s
        for _ in range(2000):
            cand = neighbor(best_m)
            sc = score_candidate(cand)
            if sc < best_s:
                best_m, best_s = cand, sc
        results.append((best_s, best_m))

    results.sort()

    # =====================================================
    # DISPLAY
    # =====================================================
    st.subheader("🏆 Top 10 Lowest-Payout Combinations")

    for s, m in results:
        combo = tuple(np.where(m == 1)[0] + 1)
        st.write(f"**{combo} → ₹{s:,}**")

    best_s, best_m = results[0]
    best_combo = tuple(np.where(best_m == 1)[0] + 1)

    counts = ind @ best_m
    uniq, cnt = np.unique(counts, return_counts=True)

    st.subheader("📊 Match Breakdown")
    st.write(dict(zip(uniq.astype(int), cnt.astype(int))))
    st.success(f"🔥 Best Combination: {best_combo} → ₹{best_s:,}")
