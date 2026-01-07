import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Expense Tracker", layout="wide")
st.title("Smart Expense Tracker + Insights")

# nicer default plotting style
plt.style.use("ggplot")

def api_get(path: str):
    r = requests.get(f"{API}{path}")
    r.raise_for_status()
    return r.json()

def api_post(path: str, payload: dict):
    return requests.post(f"{API}{path}", json=payload)

def api_delete(path: str):
    return requests.delete(f"{API}{path}")

# --- Sidebar: Add Transaction (ALWAYS AVAILABLE) ---
with st.sidebar:
    st.header("Add Transaction")
    date = st.date_input("Date")
    desc = st.text_input("Description", placeholder="e.g., Tim Hortons coffee")
    amount = st.number_input("Amount (negative = expense)", value=-5.00, step=0.50)

    if st.button("Add"):
        payload = {"date": str(date), "description": desc, "amount": float(amount)}
        r = api_post("/transactions", payload)
        if r.status_code == 200:
            st.success(f"Added (Category: {r.json().get('category')})")
            st.rerun()
        else:
            st.error(r.text)

# --- Load data ---
tx = api_get("/transactions")
df = pd.DataFrame(tx) if isinstance(tx, list) else pd.DataFrame()

has_data = not df.empty

if has_data:
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date", ascending=False)

# --- Empty state (NO st.stop) ---
if not has_data:
    st.info("Add your first transaction using the sidebar to get started.")
    st.caption("Once you add transactions, you’ll see charts, trends, projections, and delete controls here.")
    st.stop()

# --- Month Picker (makes projection actually change) ---
months = sorted(df["date"].dt.to_period("M").astype(str).unique().tolist())
selected_month = st.selectbox("Month to analyze", months, index=len(months) - 1)

ins = api_get(f"/insights?month={selected_month}")

# --- Top Metrics ---
c1, c2, c3, c4 = st.columns(4)
total_spent = ins.get("total_spent", 0.0)
projected = ins.get("projected_spending_focus_month", 0.0)

c1.metric("Total Spent (Month)", f"${total_spent:,.2f}")
c2.metric("Projected This Month", f"${projected:,.2f}")
c3.metric("Focus Month", ins.get("focus_month", selected_month))
c4.metric("Transactions", f"{len(df)}")

trend = ins.get("trend_note")
if trend:
    st.caption(trend)
else:
    st.caption("Add transactions across multiple months to get month-to-month trend notes.")

st.divider()

# --- Transactions + Delete ---
st.subheader("Transactions")

clean_df = df.copy()
clean_df["date"] = clean_df["date"].dt.date

st.dataframe(
    clean_df[["id", "date", "description", "category", "amount", "source"]],
    use_container_width=True,
    hide_index=True
)

st.subheader("Delete a Transaction")
selected_id = st.selectbox(
    "Select transaction ID",
    options=clean_df["id"].tolist(),
    format_func=lambda i: f"ID {i} — {clean_df.loc[clean_df['id']==i, 'description'].values[0]} ({clean_df.loc[clean_df['id']==i, 'amount'].values[0]})"
)

if st.button("Delete selected"):
    r = api_delete(f"/transactions/{int(selected_id)}")
    if r.status_code == 200:
        st.success(f"Deleted ID {selected_id}")
        st.rerun()
    else:
        st.error(r.text)

st.divider()

# --- Charts ---
left, right = st.columns(2)

with left:
    st.subheader("Spending by Category (Month)")
    exp = df[(df["amount"] < 0) & (df["date"].dt.to_period("M").astype(str) == selected_month)].copy()
    if not exp.empty:
        exp["spent"] = -exp["amount"]
        by_cat = exp.groupby("category")["spent"].sum().sort_values(ascending=False)
        fig = plt.figure()
        by_cat.plot(kind="bar")
        plt.xlabel("Category")
        plt.ylabel("Spent ($)")
        st.pyplot(fig)
    else:
        st.info("No expenses in this month yet.")

with right:
    st.subheader("Monthly Spending (All Months)")
    exp_all = df[df["amount"] < 0].copy()
    exp_all["spent"] = -exp_all["amount"]
    exp_all["month"] = exp_all["date"].dt.to_period("M").astype(str)
    monthly = exp_all.groupby("month")["spent"].sum().sort_index()

    if not monthly.empty:
        fig2 = plt.figure()
        monthly.plot(kind="line", marker="o")
        plt.xlabel("Month")
        plt.ylabel("Spent ($)")
        st.pyplot(fig2)
    else:
        st.info("No expenses yet.")

