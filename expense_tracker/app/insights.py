import pandas as pd

def generate_insights(transactions: list[dict], focus_month: str | None = None) -> dict:
    if not transactions:
        return {"message": "No transactions yet."}

    df = pd.DataFrame(transactions)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

    # Expenses are negative
    expenses = df[df["amount"] < 0].copy()
    expenses["spent"] = -expenses["amount"]

    # Choose month to analyze
    if focus_month is None:
        focus_month = df["month"].max()

    month_exp = expenses[expenses["month"] == focus_month].copy()

    total_spent = float(month_exp["spent"].sum()) if not month_exp.empty else 0.0

    by_category = (
        month_exp.groupby("category")["spent"].sum().sort_values(ascending=False).to_dict()
        if not month_exp.empty else {}
    )
    by_category = {k: float(v) for k, v in by_category.items()}

    # Monthly totals for trend line
    monthly = expenses.groupby("month")["spent"].sum().sort_index()
    monthly_spending = {k: float(v) for k, v in monthly.items()}

    # Trend note vs previous month
    trend_note = None
    if focus_month in monthly.index:
        idx = list(monthly.index).index(focus_month)
        if idx - 1 >= 0:
            prev_month = monthly.index[idx - 1]
            prev_val = monthly.loc[prev_month]
            cur_val = monthly.loc[focus_month]
            if prev_val != 0:
                pct = (cur_val - prev_val) / prev_val * 100
                trend_note = f"{focus_month} changed {pct:+.1f}% vs {prev_month}."

    # Projection for focus month (average daily spend so far * 30)
    projected = 0.0
    if not month_exp.empty:
        days_so_far = int(month_exp["date"].dt.day.max())
        daily_avg = month_exp["spent"].sum() / max(days_so_far, 1)
        projected = float(daily_avg * 30)

    return {
        "focus_month": focus_month,
        "total_spent": total_spent,
        "by_category": by_category,
        "monthly_spending": monthly_spending,
        "trend_note": trend_note,
        "projected_spending_focus_month": projected,
    }
