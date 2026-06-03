import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Nassau Candy | Margin Intelligence",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Dark candy-brand palette */
:root {
    --candy-pink:   #FF4B91;
    --candy-purple: #7B2FBE;
    --candy-teal:   #00C4B4;
    --candy-yellow: #FFD166;
    --bg-dark:      #0D0D1A;
    --bg-card:      #16162A;
    --text-main:    #F0EEF8;
    --text-muted:   #9B96BB;
}

/* Main background */
.stApp { background-color: var(--bg-dark); color: var(--text-main); }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #16162A 0%, #0D0D1A 100%);
    border-right: 1px solid #2a2a45;
}

/* KPI Cards */
.kpi-card {
    background: linear-gradient(135deg, #16162A 0%, #1e1e35 100%);
    border: 1px solid #2a2a45;
    border-radius: 16px;
    padding: 22px 20px;
    text-align: center;
    transition: transform 0.2s;
}
.kpi-card:hover { transform: translateY(-3px); }
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #FF4B91, #7B2FBE);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.kpi-label {
    font-size: 0.78rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-top: 4px;
}
.kpi-delta {
    font-size: 0.82rem;
    margin-top: 6px;
}
.delta-pos { color: #00C4B4; }
.delta-neg { color: #FF4B91; }

/* Section headers */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-main);
    border-left: 4px solid var(--candy-pink);
    padding-left: 12px;
    margin: 8px 0 18px 0;
}

/* Tab labels */
.stTabs [data-baseweb="tab"] {
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    color: var(--text-muted);
    padding: 10px 20px;
}
.stTabs [aria-selected="true"] {
    color: var(--candy-pink) !important;
    border-bottom: 2px solid var(--candy-pink) !important;
}

/* Dataframe */
.dataframe { background: var(--bg-card) !important; color: var(--text-main) !important; }

/* Divider */
hr { border-color: #2a2a45; margin: 8px 0; }

/* Plotly chart frames */
.js-plotly-plot { border-radius: 12px; }

/* Sidebar labels */
.sidebar-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-muted);
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────────
PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(22,22,42,0.6)",
        font=dict(family="DM Sans", color="#F0EEF8"),
        xaxis=dict(gridcolor="#2a2a45", zerolinecolor="#2a2a45"),
        yaxis=dict(gridcolor="#2a2a45", zerolinecolor="#2a2a45"),
        margin=dict(l=30, r=20, t=40, b=30),
        legend=dict(bgcolor="rgba(22,22,42,0.8)", bordercolor="#2a2a45", borderwidth=1),
        colorway=["#FF4B91", "#7B2FBE", "#00C4B4", "#FFD166", "#4B9EFF", "#FF8C42"],
    )
)
CANDY_COLORS = ["#FF4B91", "#7B2FBE", "#00C4B4", "#FFD166", "#4B9EFF", "#FF8C42", "#A8FF78"]
DIV_COLORS   = {"Chocolate": "#7B2FBE", "Sugar": "#FF4B91", "Other": "#00C4B4"}

# ─────────────────────────────────────────────
# FACTORY / PRODUCT MAPPING
# ─────────────────────────────────────────────
PRODUCT_FACTORY = {
    "Wonka Bar - Nutty Crunch Surprise":    "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows":            "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious":       "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate":           "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel":    "Wicked Choccy's",
    "Laffy Taffy":                          "Sugar Shack",
    "SweeTARTS":                            "Sugar Shack",
    "Nerds":                                "Sugar Shack",
    "Fun Dip":                              "Sugar Shack",
    "Fizzy Lifting Drinks":                 "Sugar Shack",
    "Everlasting Gobstopper":               "Secret Factory",
    "Lickable Wallpaper":                   "Secret Factory",
    "Wonka Gum":                            "Secret Factory",
    "Hair Toffee":                          "The Other Factory",
    "Kazookles":                            "The Other Factory",
}
FACTORY_COORDS = {
    "Lot's O' Nuts":      (32.881893,  -111.768036),
    "Wicked Choccy's":    (32.076176,   -81.088371),
    "Sugar Shack":        (48.11914,    -96.18115),
    "Secret Factory":     (41.446333,   -90.565487),
    "The Other Factory":  (35.1175,     -89.971107),
}

# ─────────────────────────────────────────────
# DATA LOAD & CLEAN
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("Nassau_Candy_Distributor.csv")

    # Parse dates (dd-mm-yyyy)
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
    df["Ship Date"]  = pd.to_datetime(df["Ship Date"],  dayfirst=True, errors="coerce")

    # Drop invalid rows
    df = df.dropna(subset=["Sales", "Gross Profit", "Cost", "Order Date"])
    df = df[(df["Sales"] > 0) & (df["Units"] > 0)]

    # Derived metrics
    df["Gross Margin (%)"] = (df["Gross Profit"] / df["Sales"] * 100).round(2)
    df["Profit per Unit"]  = (df["Gross Profit"] / df["Units"]).round(3)
    df["Month"]            = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    df["Quarter"]          = df["Order Date"].dt.to_period("Q").astype(str)
    df["Factory"]          = df["Product Name"].map(PRODUCT_FACTORY)

    return df

df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 8px 0;'>
        <span style='font-family:Syne; font-size:1.6rem; font-weight:800;
                     background:linear-gradient(90deg,#FF4B91,#7B2FBE);
                     -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
            🍬 Nassau Candy
        </span><br>
        <span style='color:#9B96BB; font-size:0.75rem; letter-spacing:2px; text-transform:uppercase;'>
            Margin Intelligence
        </span>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    st.markdown('<p class="sidebar-label">📅 Date Range</p>', unsafe_allow_html=True)
    min_date = df["Order Date"].min().date()
    max_date = df["Order Date"].max().date()
    date_range = st.date_input("", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date, label_visibility="collapsed")

    st.markdown('<p class="sidebar-label" style="margin-top:14px;">🏭 Division</p>', unsafe_allow_html=True)
    all_divisions = sorted(df["Division"].unique())
    sel_divisions = st.multiselect("", all_divisions, default=all_divisions, label_visibility="collapsed")

    st.markdown('<p class="sidebar-label" style="margin-top:14px;">🗺️ Region</p>', unsafe_allow_html=True)
    all_regions = sorted(df["Region"].unique())
    sel_regions = st.multiselect("", all_regions, default=all_regions, label_visibility="collapsed")

    st.markdown('<p class="sidebar-label" style="margin-top:14px;">📉 Min Gross Margin (%)</p>', unsafe_allow_html=True)
    margin_threshold = st.slider("", 0.0, 80.0, 0.0, 0.5, label_visibility="collapsed")

    st.markdown('<p class="sidebar-label" style="margin-top:14px;">🔍 Product Search</p>', unsafe_allow_html=True)
    product_search = st.text_input("", placeholder="Type product name…", label_visibility="collapsed")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<p style="color:#9B96BB; font-size:0.7rem; text-align:center;">Nassau Candy Distributor © 2025</p>',
                unsafe_allow_html=True)

# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
if len(date_range) == 2:
    start_d, end_d = date_range
else:
    start_d, end_d = min_date, max_date

fdf = df[
    (df["Order Date"].dt.date >= start_d) &
    (df["Order Date"].dt.date <= end_d) &
    (df["Division"].isin(sel_divisions)) &
    (df["Region"].isin(sel_regions)) &
    (df["Gross Margin (%)"] >= margin_threshold)
]
if product_search:
    fdf = fdf[fdf["Product Name"].str.contains(product_search, case=False, na=False)]

if fdf.empty:
    st.warning("⚠️ No data matches the current filters. Adjust the sidebar settings.")
    st.stop()

# ─────────────────────────────────────────────
# KPI HELPERS
# ─────────────────────────────────────────────
total_sales    = fdf["Sales"].sum()
total_profit   = fdf["Gross Profit"].sum()
avg_margin     = (total_profit / total_sales * 100) if total_sales else 0
total_units    = fdf["Units"].sum()
avg_ppu        = fdf["Profit per Unit"].mean()
num_products   = fdf["Product Name"].nunique()

# ─────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style='padding: 10px 0 4px 0;'>
    <span style='font-family:Syne; font-size:2rem; font-weight:800;
                 background:linear-gradient(90deg,#FF4B91,#7B2FBE,#00C4B4);
                 -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
        Product Line Profitability & Margin Performance
    </span><br>
    <span style='color:#9B96BB; font-size:0.85rem;'>
        Nassau Candy Distributor · Filtered view · {rows:,} orders
    </span>
</div>
""".format(rows=len(fdf)), unsafe_allow_html=True)

st.markdown("<hr style='margin-bottom:18px;'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)
kpis = [
    (k1, f"${total_sales:,.0f}",    "Total Revenue"),
    (k2, f"${total_profit:,.0f}",   "Gross Profit"),
    (k3, f"{avg_margin:.1f}%",      "Avg Gross Margin"),
    (k4, f"{total_units:,}",        "Units Sold"),
    (k5, f"${avg_ppu:.2f}",         "Avg Profit / Unit"),
    (k6, f"{num_products}",         "Active Products"),
]
for col, val, label in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{val}</div>
            <div class="kpi-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Product Overview",
    "🏢 Division Performance",
    "🔬 Cost Diagnostics",
    "📈 Pareto / Concentration",
    "🗺️ Factory & Geo Map",
])

# ══════════════════════════════════════════════
# TAB 1 — PRODUCT OVERVIEW
# ══════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Product-Level Profitability Leaderboard</div>', unsafe_allow_html=True)

    prod = (fdf.groupby("Product Name")
            .agg(Total_Sales=("Sales","sum"),
                 Total_Profit=("Gross Profit","sum"),
                 Total_Units=("Units","sum"),
                 Orders=("Row ID","count"))
            .reset_index())
    prod["Gross Margin (%)"]  = (prod["Total_Profit"] / prod["Total_Sales"] * 100).round(2)
    prod["Profit per Unit"]   = (prod["Total_Profit"] / prod["Total_Units"]).round(3)
    prod["Revenue Share (%)"] = (prod["Total_Sales"]  / prod["Total_Sales"].sum() * 100).round(2)
    prod["Profit Share (%)"]  = (prod["Total_Profit"] / prod["Total_Profit"].sum() * 100).round(2)
    prod["Division"]          = prod["Product Name"].map(fdf.drop_duplicates("Product Name").set_index("Product Name")["Division"])
    prod = prod.sort_values("Total_Profit", ascending=False).reset_index(drop=True)

    c1, c2 = st.columns([1.4, 1])

    with c1:
        fig = px.bar(prod, x="Total_Profit", y="Product Name", orientation="h",
                     color="Gross Margin (%)",
                     color_continuous_scale=["#7B2FBE","#FF4B91","#FFD166","#00C4B4"],
                     text=prod["Gross Margin (%)"].apply(lambda x: f"{x:.1f}%"),
                     title="Gross Profit by Product (color = margin %)",
                     template=PLOTLY_TEMPLATE)
        fig.update_traces(textposition="outside", textfont_size=10)
        fig.update_layout(yaxis=dict(autorange="reversed"), height=480,
                          coloraxis_colorbar=dict(title="Margin %"))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = px.scatter(prod, x="Total_Sales", y="Gross Margin (%)",
                          size="Total_Units", color="Division",
                          hover_name="Product Name",
                          color_discrete_map=DIV_COLORS,
                          title="Sales vs Margin (bubble = units)",
                          template=PLOTLY_TEMPLATE, size_max=50)
        fig2.add_hline(y=avg_margin, line_dash="dot", line_color="#FFD166",
                       annotation_text=f"Avg {avg_margin:.1f}%", annotation_font_color="#FFD166")
        fig2.update_layout(height=480)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title" style="margin-top:10px;">Profit per Unit Comparison</div>',
                unsafe_allow_html=True)

    fig3 = px.bar(prod.sort_values("Profit per Unit", ascending=False),
                  x="Product Name", y="Profit per Unit",
                  color="Division", color_discrete_map=DIV_COLORS,
                  template=PLOTLY_TEMPLATE, title="Profit per Unit by Product")
    fig3.update_layout(height=320, xaxis_tickangle=-35)
    st.plotly_chart(fig3, use_container_width=True)

    # Monthly trend
    st.markdown('<div class="section-title" style="margin-top:4px;">Monthly Revenue & Profit Trend</div>',
                unsafe_allow_html=True)
    monthly = fdf.groupby("Month").agg(Sales=("Sales","sum"), Profit=("Gross Profit","sum")).reset_index()
    monthly["Margin (%)"] = (monthly["Profit"] / monthly["Sales"] * 100).round(2)

    fig4 = make_subplots(specs=[[{"secondary_y": True}]])
    fig4.add_trace(go.Bar(x=monthly["Month"], y=monthly["Sales"], name="Revenue",
                          marker_color="#7B2FBE", opacity=0.75), secondary_y=False)
    fig4.add_trace(go.Bar(x=monthly["Month"], y=monthly["Profit"], name="Gross Profit",
                          marker_color="#FF4B91", opacity=0.9), secondary_y=False)
    fig4.add_trace(go.Scatter(x=monthly["Month"], y=monthly["Margin (%)"], name="Margin %",
                              line=dict(color="#FFD166", width=2.5, dash="dot"), mode="lines+markers"),
                   secondary_y=True)
    fig4.update_layout(template=PLOTLY_TEMPLATE, height=340, barmode="group",
                       legend=dict(orientation="h", y=1.12))
    fig4.update_yaxes(title_text="USD ($)", secondary_y=False)
    fig4.update_yaxes(title_text="Gross Margin (%)", secondary_y=True,
                      tickformat=".1f", showgrid=False)
    st.plotly_chart(fig4, use_container_width=True)

    # Table
    st.markdown('<div class="section-title">Full Product Table</div>', unsafe_allow_html=True)
    disp = prod[["Product Name","Division","Total_Sales","Total_Profit","Gross Margin (%)","Profit per Unit",
                 "Revenue Share (%)","Profit Share (%)","Orders"]].copy()
    disp.columns = ["Product","Division","Revenue ($)","Profit ($)","Gross Margin (%)","Profit/Unit",
                    "Rev Share (%)","Profit Share (%)","Orders"]
    disp["Revenue ($)"] = disp["Revenue ($)"].map("${:,.2f}".format)
    disp["Profit ($)"]  = disp["Profit ($)"].map("${:,.2f}".format)
    st.dataframe(disp, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 2 — DIVISION PERFORMANCE
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Division-Level KPIs</div>', unsafe_allow_html=True)

    div_agg = (fdf.groupby("Division")
               .agg(Revenue=("Sales","sum"),
                    Profit=("Gross Profit","sum"),
                    Cost=("Cost","sum"),
                    Units=("Units","sum"),
                    Orders=("Row ID","count"),
                    Products=("Product Name","nunique"))
               .reset_index())
    div_agg["Gross Margin (%)"]  = (div_agg["Profit"] / div_agg["Revenue"] * 100).round(2)
    div_agg["Profit per Unit"]   = (div_agg["Profit"] / div_agg["Units"]).round(3)
    div_agg["Rev Share (%)"]     = (div_agg["Revenue"] / div_agg["Revenue"].sum() * 100).round(1)
    div_agg["Profit Share (%)"]  = (div_agg["Profit"]  / div_agg["Profit"].sum()  * 100).round(1)

    # KPI cards per division
    dcols = st.columns(len(div_agg))
    for i, row in div_agg.iterrows():
        with dcols[i]:
            color = DIV_COLORS.get(row["Division"], "#FFD166")
            st.markdown(f"""
            <div class="kpi-card" style="border-top: 3px solid {color};">
                <div style='font-family:Syne; font-weight:700; font-size:1rem; color:{color};'>
                    {row['Division']}
                </div>
                <div class="kpi-value" style='font-size:1.5rem;'>{row['Gross Margin (%)']:.1f}%</div>
                <div class="kpi-label">Gross Margin</div>
                <hr style='margin:8px 0;'>
                <div style='font-size:0.82rem; color:#9B96BB;'>Revenue: ${row['Revenue']:,.0f}</div>
                <div style='font-size:0.82rem; color:#9B96BB;'>Profit: ${row['Profit']:,.0f}</div>
                <div style='font-size:0.82rem; color:#9B96BB;'>Units: {row['Units']:,}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        fig = px.bar(div_agg, x="Division", y=["Revenue","Profit"],
                     barmode="group",
                     color_discrete_sequence=["#7B2FBE","#FF4B91"],
                     title="Revenue vs Gross Profit by Division",
                     template=PLOTLY_TEMPLATE)
        fig.update_layout(height=360, legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = px.pie(div_agg, names="Division", values="Profit",
                      color="Division", color_discrete_map=DIV_COLORS,
                      title="Profit Contribution by Division",
                      hole=0.55, template=PLOTLY_TEMPLATE)
        fig2.update_traces(textinfo="percent+label",
                           textfont=dict(family="DM Sans"))
        fig2.update_layout(height=360)
        st.plotly_chart(fig2, use_container_width=True)

    # Margin by division over time
    st.markdown('<div class="section-title">Monthly Margin Trend by Division</div>', unsafe_allow_html=True)
    div_time = (fdf.groupby(["Month","Division"])
                .agg(S=("Sales","sum"), P=("Gross Profit","sum"))
                .reset_index())
    div_time["Margin (%)"] = (div_time["P"] / div_time["S"] * 100).round(2)
    fig3 = px.line(div_time, x="Month", y="Margin (%)", color="Division",
                   color_discrete_map=DIV_COLORS, markers=True,
                   title="Gross Margin % over Time by Division",
                   template=PLOTLY_TEMPLATE)
    fig3.update_layout(height=320)
    st.plotly_chart(fig3, use_container_width=True)

    # Region breakdown
    st.markdown('<div class="section-title">Division × Region Revenue Heatmap</div>', unsafe_allow_html=True)
    heat = fdf.pivot_table(index="Division", columns="Region", values="Sales", aggfunc="sum").fillna(0)
    fig4 = px.imshow(heat, text_auto="$.0f",
                     color_continuous_scale=["#0D0D1A","#7B2FBE","#FF4B91","#FFD166"],
                     title="Revenue Heatmap: Division × Region",
                     template=PLOTLY_TEMPLATE)
    fig4.update_layout(height=300)
    st.plotly_chart(fig4, use_container_width=True)

    # Margin by region
    st.markdown('<div class="section-title">Gross Margin (%) by Region</div>', unsafe_allow_html=True)
    reg_agg = (fdf.groupby("Region")
               .agg(Revenue=("Sales","sum"), Profit=("Gross Profit","sum"))
               .reset_index())
    reg_agg["Gross Margin (%)"] = (reg_agg["Profit"] / reg_agg["Revenue"] * 100).round(2)
    fig5 = px.bar(reg_agg.sort_values("Gross Margin (%)", ascending=False),
                  x="Region", y="Gross Margin (%)",
                  color="Gross Margin (%)",
                  color_continuous_scale=["#7B2FBE","#FF4B91","#00C4B4"],
                  template=PLOTLY_TEMPLATE, title="Average Gross Margin by Region",
                  text=reg_agg.sort_values("Gross Margin (%)", ascending=False)["Gross Margin (%)"]
                              .apply(lambda x: f"{x:.1f}%"))
    fig5.update_traces(textposition="outside")
    fig5.update_layout(height=300)
    st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 — COST DIAGNOSTICS
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Cost vs Sales Scatter — Margin Risk Landscape</div>',
                unsafe_allow_html=True)

    prod_cost = (fdf.groupby(["Product Name","Division"])
                 .agg(Sales=("Sales","sum"),
                      Cost=("Cost","sum"),
                      Profit=("Gross Profit","sum"),
                      Units=("Units","sum"))
                 .reset_index())
    prod_cost["Gross Margin (%)"] = (prod_cost["Profit"] / prod_cost["Sales"] * 100).round(2)
    prod_cost["Cost Ratio (%)"]   = (prod_cost["Cost"]   / prod_cost["Sales"] * 100).round(2)
    prod_cost["Risk Flag"] = prod_cost["Gross Margin (%)"].apply(
        lambda m: "🔴 Low Margin" if m < 50 else ("🟡 Medium" if m < 60 else "🟢 Healthy")
    )

    fig = px.scatter(prod_cost, x="Cost", y="Sales",
                     size="Units", color="Gross Margin (%)",
                     hover_name="Product Name",
                     hover_data={"Risk Flag": True, "Cost Ratio (%)": True},
                     color_continuous_scale=["#FF4B91","#FFD166","#00C4B4"],
                     title="Cost vs Revenue (bubble = units; color = gross margin %)",
                     template=PLOTLY_TEMPLATE, size_max=55)
    # Diagonal reference (break-even line)
    max_val = max(prod_cost["Cost"].max(), prod_cost["Sales"].max()) * 1.05
    fig.add_trace(go.Scatter(x=[0, max_val], y=[0, max_val],
                             mode="lines", name="Break-even",
                             line=dict(color="#9B96BB", dash="dash", width=1.5)))
    fig.update_layout(height=480)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section-title">Cost Ratio by Product</div>', unsafe_allow_html=True)
        fig2 = px.bar(prod_cost.sort_values("Cost Ratio (%)", ascending=False),
                      x="Product Name", y="Cost Ratio (%)",
                      color="Division", color_discrete_map=DIV_COLORS,
                      template=PLOTLY_TEMPLATE, title="Cost Ratio (Cost / Revenue × 100)")
        fig2.add_hline(y=50, line_dash="dot", line_color="#FFD166",
                       annotation_text="50% threshold", annotation_font_color="#FFD166")
        fig2.update_layout(height=360, xaxis_tickangle=-40)
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        st.markdown('<div class="section-title">Margin Risk Flags</div>', unsafe_allow_html=True)
        risk_counts = prod_cost["Risk Flag"].value_counts().reset_index()
        risk_counts.columns = ["Flag","Count"]
        fig3 = px.pie(risk_counts, names="Flag", values="Count",
                      color_discrete_sequence=["#FF4B91","#FFD166","#00C4B4"],
                      title="Products by Margin Risk Category",
                      hole=0.5, template=PLOTLY_TEMPLATE)
        fig3.update_layout(height=360)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="section-title">Margin Volatility by Product (Monthly Std Dev)</div>',
                unsafe_allow_html=True)
    vol = (fdf.groupby(["Product Name","Month"])
           .agg(S=("Sales","sum"), P=("Gross Profit","sum"))
           .reset_index())
    vol["m"] = (vol["P"] / vol["S"] * 100)
    vol2 = vol.groupby("Product Name")["m"].std().reset_index()
    vol2.columns = ["Product Name","Margin StdDev (%)"]
    vol2["Division"] = vol2["Product Name"].map(
        fdf.drop_duplicates("Product Name").set_index("Product Name")["Division"])
    vol2 = vol2.sort_values("Margin StdDev (%)", ascending=False)
    fig4 = px.bar(vol2, x="Product Name", y="Margin StdDev (%)",
                  color="Division", color_discrete_map=DIV_COLORS,
                  template=PLOTLY_TEMPLATE, title="Margin Volatility (Std Dev across months)")
    fig4.update_layout(height=320, xaxis_tickangle=-35)
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="section-title">⚠️ Products Needing Action</div>', unsafe_allow_html=True)
    low_margin = prod_cost[prod_cost["Gross Margin (%)"] < 55].sort_values("Gross Margin (%)")
    low_margin["Recommendation"] = low_margin["Gross Margin (%)"].apply(
        lambda m: "🚫 Discontinuation Review" if m < 45 else
                  ("💰 Cost Renegotiation"    if m < 50 else "📊 Repricing Needed")
    )
    if low_margin.empty:
        st.success("✅ All products are above the 55% margin threshold with current filters.")
    else:
        disp_low = low_margin[["Product Name","Division","Sales","Cost","Gross Margin (%)","Recommendation"]].copy()
        disp_low["Sales"] = disp_low["Sales"].map("${:,.2f}".format)
        disp_low["Cost"]  = disp_low["Cost"].map("${:,.2f}".format)
        st.dataframe(disp_low, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 4 — PARETO / CONCENTRATION
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Pareto Analysis — Revenue & Profit Concentration</div>',
                unsafe_allow_html=True)

    def pareto_df(df_in, value_col, group_col="Product Name"):
        g = df_in.groupby(group_col)[value_col].sum().sort_values(ascending=False).reset_index()
        g["cumsum"]   = g[value_col].cumsum()
        g["cum_pct"]  = g["cumsum"] / g[value_col].sum() * 100
        g["bar_pct"]  = g[value_col] / g[value_col].sum() * 100
        return g

    rev_pareto = pareto_df(fdf, "Sales")
    prf_pareto = pareto_df(fdf, "Gross Profit")

    def pareto_80(df_par):
        return df_par[df_par["cum_pct"] <= 80].shape[0]

    c1, c2 = st.columns(2)

    with c1:
        n80_rev = pareto_80(rev_pareto)
        st.info(f"**{n80_rev}** of {rev_pareto.shape[0]} products generate 80% of **Revenue**")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=rev_pareto["Product Name"], y=rev_pareto["bar_pct"],
                             name="Rev %", marker_color="#7B2FBE", opacity=0.85), secondary_y=False)
        fig.add_trace(go.Scatter(x=rev_pareto["Product Name"], y=rev_pareto["cum_pct"],
                                 name="Cumulative %", line=dict(color="#FFD166", width=2.5)),
                      secondary_y=True)
        fig.add_hline(y=80, line_dash="dot", line_color="#FF4B91", secondary_y=True,
                      annotation_text="80%", annotation_font_color="#FF4B91")
        fig.update_layout(title="Revenue Pareto", template=PLOTLY_TEMPLATE, height=380,
                          xaxis_tickangle=-40, legend=dict(orientation="h", y=1.12))
        fig.update_yaxes(title_text="Share (%)", secondary_y=False)
        fig.update_yaxes(title_text="Cumulative (%)", secondary_y=True, showgrid=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        n80_prf = pareto_80(prf_pareto)
        st.info(f"**{n80_prf}** of {prf_pareto.shape[0]} products generate 80% of **Profit**")
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(go.Bar(x=prf_pareto["Product Name"], y=prf_pareto["bar_pct"],
                              name="Profit %", marker_color="#FF4B91", opacity=0.85), secondary_y=False)
        fig2.add_trace(go.Scatter(x=prf_pareto["Product Name"], y=prf_pareto["cum_pct"],
                                  name="Cumulative %", line=dict(color="#00C4B4", width=2.5)),
                       secondary_y=True)
        fig2.add_hline(y=80, line_dash="dot", line_color="#FFD166", secondary_y=True,
                       annotation_text="80%", annotation_font_color="#FFD166")
        fig2.update_layout(title="Profit Pareto", template=PLOTLY_TEMPLATE, height=380,
                           xaxis_tickangle=-40, legend=dict(orientation="h", y=1.12))
        fig2.update_yaxes(title_text="Share (%)", secondary_y=False)
        fig2.update_yaxes(title_text="Cumulative (%)", secondary_y=True, showgrid=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Revenue vs Profit share divergence
    st.markdown('<div class="section-title">Revenue vs Profit Share Divergence</div>', unsafe_allow_html=True)
    share_df = (fdf.groupby(["Product Name","Division"])
                .agg(Revenue=("Sales","sum"), Profit=("Gross Profit","sum"))
                .reset_index())
    share_df["Rev Share (%)"]    = share_df["Revenue"] / share_df["Revenue"].sum() * 100
    share_df["Profit Share (%)"] = share_df["Profit"]  / share_df["Profit"].sum()  * 100
    share_df["Gap"]              = (share_df["Profit Share (%)"] - share_df["Rev Share (%)"]).round(2)
    share_df = share_df.sort_values("Gap", ascending=False)

    fig3 = go.Figure()
    for _, r in share_df.iterrows():
        color = "#00C4B4" if r["Gap"] >= 0 else "#FF4B91"
        fig3.add_trace(go.Bar(x=[r["Product Name"]], y=[r["Gap"]],
                              marker_color=color, showlegend=False,
                              name=r["Product Name"]))
    fig3.add_hline(y=0, line_color="#9B96BB", line_width=1)
    fig3.update_layout(title="Profit Share − Revenue Share (positive = efficient, negative = drag)",
                       template=PLOTLY_TEMPLATE, height=340,
                       xaxis_tickangle=-40)
    st.plotly_chart(fig3, use_container_width=True)

    # State-level revenue concentration
    st.markdown('<div class="section-title">Top 15 States by Revenue (Congestion Risk)</div>',
                unsafe_allow_html=True)
    state_agg = (fdf.groupby("State/Province")
                 .agg(Revenue=("Sales","sum"), Profit=("Gross Profit","sum"))
                 .reset_index()
                 .sort_values("Revenue", ascending=False)
                 .head(15))
    state_agg["Margin (%)"] = (state_agg["Profit"] / state_agg["Revenue"] * 100).round(1)
    fig4 = px.bar(state_agg, x="State/Province", y="Revenue",
                  color="Margin (%)",
                  color_continuous_scale=["#7B2FBE","#FF4B91","#FFD166","#00C4B4"],
                  template=PLOTLY_TEMPLATE, title="Revenue Concentration by State",
                  text=state_agg["Margin (%)"].apply(lambda x: f"{x:.1f}%"))
    fig4.update_traces(textposition="outside")
    fig4.update_layout(height=360, xaxis_tickangle=-35)
    st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 5 — FACTORY & GEO MAP
# ══════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">Factory Performance Map</div>', unsafe_allow_html=True)

    factory_agg = (fdf.groupby("Factory")
                   .agg(Revenue=("Sales","sum"),
                        Profit=("Gross Profit","sum"),
                        Units=("Units","sum"),
                        Products=("Product Name","nunique"))
                   .reset_index())
    factory_agg["Gross Margin (%)"] = (factory_agg["Profit"] / factory_agg["Revenue"] * 100).round(2)
    factory_agg["Lat"] = factory_agg["Factory"].map(lambda f: FACTORY_COORDS[f][0] if f in FACTORY_COORDS else None)
    factory_agg["Lon"] = factory_agg["Factory"].map(lambda f: FACTORY_COORDS[f][1] if f in FACTORY_COORDS else None)
    factory_agg = factory_agg.dropna(subset=["Lat","Lon"])

    fig_map = px.scatter_mapbox(
        factory_agg,
        lat="Lat", lon="Lon",
        size="Revenue",
        color="Gross Margin (%)",
        hover_name="Factory",
        hover_data={"Revenue": ":$,.0f", "Profit": ":$,.0f",
                    "Gross Margin (%)": ":.1f", "Products": True, "Units": True,
                    "Lat": False, "Lon": False},
        color_continuous_scale=["#FF4B91","#FFD166","#00C4B4"],
        size_max=60,
        zoom=3.5,
        mapbox_style="carto-darkmatter",
        title="Factory Locations — bubble size = Revenue, color = Gross Margin %",
    )
    fig_map.update_layout(
        template=PLOTLY_TEMPLATE,
        height=480,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Factory KPI table
    st.markdown('<div class="section-title">Factory KPI Summary</div>', unsafe_allow_html=True)
    fac_disp = factory_agg[["Factory","Revenue","Profit","Gross Margin (%)","Units","Products"]].copy()
    fac_disp["Revenue"] = fac_disp["Revenue"].map("${:,.2f}".format)
    fac_disp["Profit"]  = fac_disp["Profit"].map("${:,.2f}".format)
    fac_disp = fac_disp.sort_values("Gross Margin (%)", ascending=False)
    st.dataframe(fac_disp, use_container_width=True, hide_index=True)

    # Shipmode analysis
    st.markdown('<div class="section-title">Ship Mode — Revenue & Margin</div>', unsafe_allow_html=True)
    ship = (fdf.groupby("Ship Mode")
            .agg(Revenue=("Sales","sum"), Profit=("Gross Profit","sum"), Orders=("Row ID","count"))
            .reset_index())
    ship["Margin (%)"] = (ship["Profit"] / ship["Revenue"] * 100).round(2)

    c1, c2 = st.columns(2)
    with c1:
        fig_s1 = px.pie(ship, names="Ship Mode", values="Revenue",
                        color_discrete_sequence=CANDY_COLORS,
                        title="Revenue by Ship Mode", hole=0.5,
                        template=PLOTLY_TEMPLATE)
        fig_s1.update_layout(height=320)
        st.plotly_chart(fig_s1, use_container_width=True)
    with c2:
        fig_s2 = px.bar(ship, x="Ship Mode", y="Margin (%)",
                        color="Ship Mode", color_discrete_sequence=CANDY_COLORS,
                        title="Gross Margin % by Ship Mode",
                        template=PLOTLY_TEMPLATE,
                        text=ship["Margin (%)"].apply(lambda x: f"{x:.1f}%"))
        fig_s2.update_traces(textposition="outside")
        fig_s2.update_layout(height=320)
        st.plotly_chart(fig_s2, use_container_width=True)

    # Quarterly heatmap
    st.markdown('<div class="section-title">Quarterly Profit Heatmap by Product</div>', unsafe_allow_html=True)
    q_heat = fdf.pivot_table(index="Product Name", columns="Quarter",
                             values="Gross Profit", aggfunc="sum").fillna(0)
    fig_qh = px.imshow(q_heat, text_auto="$.0f",
                       color_continuous_scale=["#0D0D1A","#7B2FBE","#FF4B91","#FFD166"],
                       title="Quarterly Gross Profit: Product × Quarter",
                       template=PLOTLY_TEMPLATE)
    fig_qh.update_layout(height=400)
    st.plotly_chart(fig_qh, use_container_width=True)
