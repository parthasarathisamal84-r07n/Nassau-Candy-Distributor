"""
Nassau Candy Distributor
Product Line Profitability & Margin Performance Dashboard
============================================================
A Streamlit web app — deployable on Streamlit Community Cloud.

HOW TO DEPLOY:
1. Push this file + Nassau_Candy_Distributor.csv + requirements.txt
   to a GitHub repo (same folder).
2. Go to https://share.streamlit.io  →  "New app"
3. Point it at this file (app.py) in your repo.
4. Done — no google.colab, no extra setup needed.

HOW TO RUN LOCALLY:
    pip install -r requirements.txt
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Nassau Candy — Profitability Dashboard",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded",
)

PALETTE = {"Chocolate": "#6B3A2A", "Sugar": "#E87C6C", "Other": "#4a8a68"}
ACCENT = "#2C5F8A"

st.markdown("""
<style>
.block-container {padding-top: 1.5rem;}
[data-testid="stMetricValue"] {font-size: 26px;}
h1, h2, h3 {color: #3B2010;}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING  (cached so it only runs once per session)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    # Look for the CSV next to this script — works both locally and on Streamlit Cloud
    here = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(here, "Nassau_Candy_Distributor.csv")

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    # Parse dates (file uses DD-MM-YYYY)
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
    df["Ship Date"]  = pd.to_datetime(df["Ship Date"],  dayfirst=True, errors="coerce")

    # Clean invalid rows
    df = df.dropna(subset=["Sales", "Cost", "Gross Profit", "Units", "Order Date"])
    df = df[(df["Sales"] > 0) & (df["Units"] > 0)]

    # Derived KPIs
    df["Gross Margin %"]  = (df["Gross Profit"] / df["Sales"] * 100).round(2)
    df["Profit per Unit"] = (df["Gross Profit"] / df["Units"]).round(2)
    df["Cost per Unit"]   = (df["Cost"] / df["Units"]).round(2)
    df["Month"]           = df["Order Date"].dt.to_period("M").dt.to_timestamp()

    return df


df_raw = load_data()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — FILTERS
# ══════════════════════════════════════════════════════════════════════════════
st.sidebar.title("🍬 Nassau Candy")
st.sidebar.caption("Profitability & Margin Dashboard")
st.sidebar.markdown("---")

st.sidebar.subheader("Filters")

# Date range
min_date, max_date = df_raw["Order Date"].min().date(), df_raw["Order Date"].max().date()
date_range = st.sidebar.date_input(
    "Order date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Division filter
divisions = sorted(df_raw["Division"].unique())
selected_divisions = st.sidebar.multiselect(
    "Division", options=divisions, default=divisions
)

# Margin threshold slider
margin_min, margin_max = float(df_raw["Gross Margin %"].min()), float(df_raw["Gross Margin %"].max())
margin_threshold = st.sidebar.slider(
    "Minimum Gross Margin %",
    min_value=0.0, max_value=100.0,
    value=0.0, step=1.0,
)

# Product search
product_search = st.sidebar.text_input("🔍 Search product name", "")

st.sidebar.markdown("---")
st.sidebar.caption(f"Data range: {min_date} → {max_date}")
st.sidebar.caption(f"{len(df_raw):,} total order lines")

# ── Apply filters ──────────────────────────────────────────────────────────────
df = df_raw.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    df = df[(df["Order Date"].dt.date >= start) & (df["Order Date"].dt.date <= end)]

if selected_divisions:
    df = df[df["Division"].isin(selected_divisions)]

df = df[df["Gross Margin %"] >= margin_threshold]

if product_search:
    df = df[df["Product Name"].str.contains(product_search, case=False, na=False)]

if df.empty:
    st.warning("No data matches the current filters. Try widening your filter selection.")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# AGGREGATIONS  (recomputed on filtered data)
# ══════════════════════════════════════════════════════════════════════════════
prod = (df.groupby(["Division", "Product Name"])
          .agg(Total_Sales=("Sales", "sum"),
               Total_Cost=("Cost", "sum"),
               Total_Gross_Profit=("Gross Profit", "sum"),
               Total_Units=("Units", "sum"),
               Order_Count=("Row ID", "count"))
          .reset_index())
prod["Gross Margin %"]       = (prod["Total_Gross_Profit"] / prod["Total_Sales"] * 100).round(2)
prod["Profit per Unit"]      = (prod["Total_Gross_Profit"] / prod["Total_Units"]).round(2)
prod["Revenue Contribution"] = (prod["Total_Sales"] / prod["Total_Sales"].sum() * 100).round(2)
prod["Profit Contribution"]  = (prod["Total_Gross_Profit"] / prod["Total_Gross_Profit"].sum() * 100).round(2)
prod = prod.sort_values("Total_Gross_Profit", ascending=False).reset_index(drop=True)

div = (df.groupby("Division")
         .agg(Total_Sales=("Sales", "sum"),
              Total_Cost=("Cost", "sum"),
              Total_Gross_Profit=("Gross Profit", "sum"),
              Total_Units=("Units", "sum"))
         .reset_index())
div["Gross Margin %"] = (div["Total_Gross_Profit"] / div["Total_Sales"] * 100).round(2)

total_sales = df["Sales"].sum()
total_gp    = df["Gross Profit"].sum()
overall_margin = total_gp / total_sales * 100 if total_sales else 0


# ══════════════════════════════════════════════════════════════════════════════
# HEADER + KPI ROW
# ══════════════════════════════════════════════════════════════════════════════
st.title("Product Line Profitability & Margin Performance")
st.caption("Nassau Candy Distributor — interactive analytics dashboard")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Revenue", f"${total_sales:,.0f}")
k2.metric("Total Gross Profit", f"${total_gp:,.0f}")
k3.metric("Overall Margin", f"{overall_margin:.1f}%")
k4.metric("Orders", f"{df['Row ID'].nunique():,}")
k5.metric("Products", f"{prod.shape[0]}")

st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# TABS  (mirrors the original dashboard modules)
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🏆 Product Profitability",
    "🏢 Division Performance",
    "📐 Cost vs Margin Diagnostics",
    "📈 Profit Concentration (Pareto)",
])

# ── TAB 1 : OVERVIEW ───────────────────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        fig = go.Figure()
        fig.add_bar(x=div["Division"], y=div["Total_Sales"], name="Revenue",
                    marker_color=[PALETTE.get(d, "#999") for d in div["Division"]])
        fig.add_bar(x=div["Division"], y=div["Total_Gross_Profit"], name="Gross Profit",
                    marker_color=[PALETTE.get(d, "#999") for d in div["Division"]],
                    opacity=0.5)
        fig.update_layout(title="Revenue vs Gross Profit by Division",
                           barmode="group", height=380)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(div.sort_values("Gross Margin %"), x="Gross Margin %", y="Division",
                      orientation="h", color="Division",
                      color_discrete_map=PALETTE, text="Gross Margin %")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.add_vline(x=overall_margin, line_dash="dash", line_color=ACCENT,
                      annotation_text=f"Avg {overall_margin:.1f}%")
        fig.update_layout(title="Gross Margin % by Division", height=380, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.pie(div, names="Division", values="Total_Sales",
                      color="Division", color_discrete_map=PALETTE,
                      title="Revenue Share by Division", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        fig = px.pie(div, names="Division", values="Total_Gross_Profit",
                      color="Division", color_discrete_map=PALETTE,
                      title="Profit Share by Division", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    # Monthly trend
    monthly = df.groupby(["Month", "Division"]).agg(
        Sales=("Sales", "sum"), GP=("Gross Profit", "sum")
    ).reset_index()
    monthly["Margin %"] = (monthly["GP"] / monthly["Sales"] * 100).round(2)

    fig = px.line(monthly, x="Month", y="Sales", color="Division",
                   color_discrete_map=PALETTE, markers=True,
                   title="Monthly Revenue Trend by Division")
    st.plotly_chart(fig, use_container_width=True)

# ── TAB 2 : PRODUCT PROFITABILITY ──────────────────────────────────────────────
with tab2:
    sort_option = st.selectbox(
        "Sort leaderboard by",
        ["Total_Gross_Profit", "Gross Margin %", "Total_Sales", "Profit per Unit"],
        index=0,
    )
    prod_sorted = prod.sort_values(sort_option, ascending=True)

    fig = px.bar(prod_sorted, x=sort_option, y="Product Name", orientation="h",
                  color="Division", color_discrete_map=PALETTE,
                  text=sort_option,
                  title=f"Product Leaderboard — sorted by {sort_option}")
    fig.update_traces(texttemplate="%{text:,.1f}", textposition="outside")
    fig.update_layout(height=max(400, len(prod_sorted) * 35))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Profit & Revenue Contribution")
    fig = px.scatter(prod, x="Revenue Contribution", y="Profit Contribution",
                      size="Total_Units", color="Division", color_discrete_map=PALETTE,
                      hover_name="Product Name",
                      title="Revenue Contribution vs Profit Contribution (bubble = units sold)")
    fig.add_shape(type="line", x0=0, y0=0, x1=prod["Revenue Contribution"].max(),
                  y1=prod["Revenue Contribution"].max(),
                  line=dict(dash="dash", color="gray"))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Product Detail Table")
    st.dataframe(
        prod.style.background_gradient(subset=["Gross Margin %"], cmap="RdYlGn")
                  .format({
                      "Total_Sales": "${:,.2f}",
                      "Total_Cost": "${:,.2f}",
                      "Total_Gross_Profit": "${:,.2f}",
                      "Profit per Unit": "${:,.2f}",
                      "Gross Margin %": "{:.1f}%",
                      "Revenue Contribution": "{:.1f}%",
                      "Profit Contribution": "{:.1f}%",
                  }),
        use_container_width=True,
        height=420,
    )

# ── TAB 3 : DIVISION PERFORMANCE ───────────────────────────────────────────────
with tab3:
    fig = go.Figure()
    fig.add_bar(x=div["Division"], y=div["Total_Cost"], name="Cost",
                marker_color="lightgray")
    fig.add_bar(x=div["Division"], y=div["Total_Gross_Profit"], name="Gross Profit",
                marker_color=[PALETTE.get(d, "#999") for d in div["Division"]])
    fig.update_layout(barmode="stack", title="Revenue Breakdown — Cost vs Profit", height=420)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Division Summary Table")
    div_display = div.copy()
    div_display["Revenue Contribution %"] = (div_display["Total_Sales"] / div_display["Total_Sales"].sum() * 100).round(1)
    div_display["Profit Contribution %"]  = (div_display["Total_Gross_Profit"] / div_display["Total_Gross_Profit"].sum() * 100).round(1)
    st.dataframe(
        div_display.style.format({
            "Total_Sales": "${:,.2f}", "Total_Cost": "${:,.2f}",
            "Total_Gross_Profit": "${:,.2f}", "Gross Margin %": "{:.1f}%",
            "Revenue Contribution %": "{:.1f}%", "Profit Contribution %": "{:.1f}%",
        }),
        use_container_width=True,
    )

# ── TAB 4 : COST VS MARGIN DIAGNOSTICS ─────────────────────────────────────────
with tab4:
    c1, c2 = st.columns(2)

    with c1:
        fig = px.scatter(prod, x="Total_Cost", y="Total_Sales", color="Division",
                          color_discrete_map=PALETTE, size="Total_Units",
                          hover_name="Product Name",
                          title="Cost vs Sales — Margin Risk Diagnostics")
        max_val = max(prod["Total_Sales"].max(), prod["Total_Cost"].max()) * 1.05
        fig.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val,
                      line=dict(dash="dash", color="black"))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        pm = prod.sort_values("Gross Margin %", ascending=True)
        fig = px.bar(pm, x="Gross Margin %", y="Product Name", orientation="h",
                      color="Division", color_discrete_map=PALETTE,
                      title="Gross Margin % by Product")
        fig.add_vline(x=overall_margin, line_dash="dash", line_color=ACCENT)
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("⚠️ Margin Risk Flags")
    risk_threshold = overall_margin * 0.9
    risk = prod[prod["Gross Margin %"] < risk_threshold][
        ["Product Name", "Division", "Gross Margin %", "Total_Sales", "Total_Gross_Profit"]
    ].sort_values("Gross Margin %")

    if risk.empty:
        st.success("No products currently fall below the margin risk threshold.")
    else:
        st.caption(f"Threshold: below {risk_threshold:.1f}% (90% of portfolio average {overall_margin:.1f}%)")
        st.dataframe(
            risk.style.background_gradient(subset=["Gross Margin %"], cmap="Reds_r")
                      .format({"Gross Margin %": "{:.1f}%", "Total_Sales": "${:,.2f}", "Total_Gross_Profit": "${:,.2f}"}),
            use_container_width=True,
        )

# ── TAB 5 : PARETO ──────────────────────────────────────────────────────────────
with tab5:
    c1, c2 = st.columns(2)

    with c1:
        p_rev = prod.sort_values("Total_Sales", ascending=False).reset_index(drop=True)
        p_rev["Cum Rev %"] = (p_rev["Total_Sales"].cumsum() / p_rev["Total_Sales"].sum() * 100).round(1)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_bar(x=p_rev["Product Name"], y=p_rev["Total_Sales"], name="Revenue",
                    marker_color=[PALETTE.get(d, "#999") for d in p_rev["Division"]],
                    secondary_y=False)
        fig.add_trace(go.Scatter(x=p_rev["Product Name"], y=p_rev["Cum Rev %"],
                                  name="Cumulative %", mode="lines+markers",
                                  line=dict(color=ACCENT)), secondary_y=True)
        fig.add_hline(y=80, line_dash="dash", line_color="red", secondary_y=True)
        fig.update_layout(title="Pareto — Revenue Concentration", height=450)
        st.plotly_chart(fig, use_container_width=True)

        n80_rev = int((p_rev["Cum Rev %"] < 80).sum()) + 1
        st.info(f"**{n80_rev} product(s)** drive 80% of total revenue.")

    with c2:
        p_prf = prod.sort_values("Total_Gross_Profit", ascending=False).reset_index(drop=True)
        p_prf["Cum Prf %"] = (p_prf["Total_Gross_Profit"].cumsum() / p_prf["Total_Gross_Profit"].sum() * 100).round(1)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_bar(x=p_prf["Product Name"], y=p_prf["Total_Gross_Profit"], name="Gross Profit",
                    marker_color=[PALETTE.get(d, "#999") for d in p_prf["Division"]],
                    secondary_y=False)
        fig.add_trace(go.Scatter(x=p_prf["Product Name"], y=p_prf["Cum Prf %"],
                                  name="Cumulative %", mode="lines+markers",
                                  line=dict(color="#2E8B57")), secondary_y=True)
        fig.add_hline(y=80, line_dash="dash", line_color="red", secondary_y=True)
        fig.update_layout(title="Pareto — Profit Concentration", height=450)
        st.plotly_chart(fig, use_container_width=True)

        n80_prf = int((p_prf["Cum Prf %"] < 80).sum()) + 1
        st.info(f"**{n80_prf} product(s)** drive 80% of total profit.")

    st.subheader("Concentration Table")
    conc = p_rev[["Product Name", "Division", "Total_Sales", "Revenue Contribution", "Cum Rev %"]].copy()
    conc = conc.merge(
        p_prf[["Product Name", "Total_Gross_Profit", "Profit Contribution", "Cum Prf %"]],
        on="Product Name"
    )
    st.dataframe(
        conc.style.format({
            "Total_Sales": "${:,.2f}", "Revenue Contribution": "{:.1f}%", "Cum Rev %": "{:.1f}%",
            "Total_Gross_Profit": "${:,.2f}", "Profit Contribution": "{:.1f}%", "Cum Prf %": "{:.1f}%",
        }),
        use_container_width=True,
    )

st.markdown("---")
st.caption("Nassau Candy Distributor · Product Line Profitability & Margin Performance Analysis")
