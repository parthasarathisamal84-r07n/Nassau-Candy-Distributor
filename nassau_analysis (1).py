"""
Nassau Candy Distributor
Product Line Profitability & Margin Performance Analysis
=========================================================
Full EDA + KPI + Pareto + Division Diagnostics
Outputs: /outputs/ folder with all charts + summary CSV
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import seaborn as sns
import warnings, os

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "Nassau_Candy_Distributor.csv")
OUT_DIR   = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Theme ──────────────────────────────────────────────────────────────────────
PALETTE   = {"Chocolate": "#6B3A2A", "Sugar": "#E87C6C", "Other": "#A8C8A0"}
DIV_COLORS = list(PALETTE.values())
BG        = "#FAFAF8"
ACCENT    = "#2C5F8A"

def style_fig(fig, ax_list=None):
    fig.patch.set_facecolor(BG)
    if ax_list is not None:
        for ax in ax_list:
            ax.set_facecolor(BG)
            ax.spines[["top","right"]].set_visible(False)
            ax.tick_params(labelsize=9)

def save(name):
    path = os.path.join(OUT_DIR, name)
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close("all")
    print(f"  ✓  {name}")

# ══════════════════════════════════════════════════════════════════════════════
# 1.  LOAD & CLEAN
# ══════════════════════════════════════════════════════════════════════════════
print("\n[1/7] Loading & cleaning data …")

df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()

# Parse dates
df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
df["Ship Date"]  = pd.to_datetime(df["Ship Date"],  dayfirst=True, errors="coerce")

# Drop invalid rows
before = len(df)
df = df.dropna(subset=["Sales","Cost","Gross Profit","Units"])
df = df[(df["Sales"] > 0) & (df["Units"] > 0)]
print(f"  Rows after cleaning: {len(df):,}  (dropped {before-len(df)})")

# Derived KPIs
df["Gross Margin %"]  = (df["Gross Profit"] / df["Sales"] * 100).round(2)
df["Profit per Unit"] = (df["Gross Profit"] / df["Units"]).round(2)
df["Cost per Unit"]   = (df["Cost"]         / df["Units"]).round(2)
df["Sales per Unit"]  = (df["Sales"]        / df["Units"]).round(2)

# Year / Month
df["Year"]  = df["Order Date"].dt.year
df["Month"] = df["Order Date"].dt.to_period("M")

print(f"  Date range: {df['Order Date'].min().date()} → {df['Order Date'].max().date()}")
print(f"  Divisions:  {sorted(df['Division'].unique())}")
print(f"  Products:   {df['Product Name'].nunique()}")

# ══════════════════════════════════════════════════════════════════════════════
# 2.  PRODUCT-LEVEL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print("\n[2/7] Product-level aggregation …")

prod = (df.groupby(["Division","Product Name"])
          .agg(
              Total_Sales        = ("Sales","sum"),
              Total_Cost         = ("Cost","sum"),
              Total_Gross_Profit = ("Gross Profit","sum"),
              Total_Units        = ("Units","sum"),
              Order_Count        = ("Row ID","count"),
          )
          .reset_index())

prod["Gross Margin %"]      = (prod["Total_Gross_Profit"] / prod["Total_Sales"] * 100).round(2)
prod["Profit per Unit"]     = (prod["Total_Gross_Profit"] / prod["Total_Units"]).round(2)
prod["Revenue Contribution"]= (prod["Total_Sales"]        / prod["Total_Sales"].sum() * 100).round(2)
prod["Profit Contribution"] = (prod["Total_Gross_Profit"] / prod["Total_Gross_Profit"].sum() * 100).round(2)
prod = prod.sort_values("Total_Gross_Profit", ascending=False).reset_index(drop=True)

prod.to_csv(os.path.join(OUT_DIR, "product_summary.csv"), index=False)
print("  Product summary saved.")

# ══════════════════════════════════════════════════════════════════════════════
# 3.  DIVISION-LEVEL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print("\n[3/7] Division-level aggregation …")

div = (df.groupby("Division")
         .agg(
             Total_Sales        = ("Sales","sum"),
             Total_Cost         = ("Cost","sum"),
             Total_Gross_Profit = ("Gross Profit","sum"),
             Total_Units        = ("Units","sum"),
             Order_Count        = ("Row ID","count"),
         )
         .reset_index())

div["Gross Margin %"]       = (div["Total_Gross_Profit"] / div["Total_Sales"] * 100).round(2)
div["Profit per Unit"]      = (div["Total_Gross_Profit"] / div["Total_Units"]).round(2)
div["Revenue Contribution"] = (div["Total_Sales"]        / div["Total_Sales"].sum() * 100).round(2)
div["Profit Contribution"]  = (div["Total_Gross_Profit"] / div["Total_Gross_Profit"].sum() * 100).round(2)

div.to_csv(os.path.join(OUT_DIR, "division_summary.csv"), index=False)
print(div[["Division","Total_Sales","Total_Gross_Profit","Gross Margin %"]].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════════
# 4.  CHART SUITE
# ══════════════════════════════════════════════════════════════════════════════
print("\n[4/7] Generating charts …")

# ── 4A: KPI Summary Cards (text figure) ───────────────────────────────────────
fig, axes = plt.subplots(1, 4, figsize=(14, 3))
fig.patch.set_facecolor(BG)
kpis = [
    ("Total Revenue",    f"${df['Sales'].sum()/1e3:.1f}K",       ACCENT),
    ("Total Gross Profit", f"${df['Gross Profit'].sum()/1e3:.1f}K", "#2E8B57"),
    ("Overall Margin",   f"{(df['Gross Profit'].sum()/df['Sales'].sum()*100):.1f}%", "#B5651D"),
    ("Total Orders",     f"{df['Row ID'].nunique():,}",           "#6B3A2A"),
]
for ax, (label, val, col) in zip(axes, kpis):
    ax.set_facecolor(col)
    ax.text(0.5, 0.62, val,  ha="center", va="center", fontsize=24, fontweight="bold",
            color="white", transform=ax.transAxes)
    ax.text(0.5, 0.25, label, ha="center", va="center", fontsize=11, color="white",
            transform=ax.transAxes)
    ax.axis("off")
fig.suptitle("Nassau Candy — Key Performance Indicators", fontsize=14, fontweight="bold", y=1.02)
save("01_kpi_cards.png")

# ── 4B: Revenue vs Profit by Division (grouped bar) ──────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(div))
w = 0.35
bars1 = ax.bar(x - w/2, div["Total_Sales"],        w, label="Revenue",      color=[PALETTE[d] for d in div["Division"]], alpha=0.9)
bars2 = ax.bar(x + w/2, div["Total_Gross_Profit"], w, label="Gross Profit", color=[PALETTE[d] for d in div["Division"]], alpha=0.5)
ax.set_xticks(x); ax.set_xticklabels(div["Division"], fontsize=11)
ax.set_ylabel("USD ($)")
ax.set_title("Revenue vs Gross Profit by Division", fontweight="bold")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"${v:,.0f}"))
ax.legend(["Revenue","Gross Profit"])
for b in bars1: ax.text(b.get_x()+b.get_width()/2, b.get_height()+50, f"${b.get_height():,.0f}", ha="center", va="bottom", fontsize=8)
for b in bars2: ax.text(b.get_x()+b.get_width()/2, b.get_height()+50, f"${b.get_height():,.0f}", ha="center", va="bottom", fontsize=8)
style_fig(fig, [ax]); save("02_division_revenue_profit.png")

# ── 4C: Gross Margin % by Division (horizontal bar) ───────────────────────────
fig, ax = plt.subplots(figsize=(7, 4))
colors = [PALETTE[d] for d in div.sort_values("Gross Margin %")["Division"]]
bars = ax.barh(div.sort_values("Gross Margin %")["Division"],
               div.sort_values("Gross Margin %")["Gross Margin %"],
               color=colors, edgecolor="white", linewidth=0.5)
for b in bars:
    ax.text(b.get_width()+0.3, b.get_y()+b.get_height()/2,
            f"{b.get_width():.1f}%", va="center", fontsize=10)
ax.set_xlabel("Gross Margin (%)")
ax.set_title("Gross Margin % by Division", fontweight="bold")
ax.axvline(df["Gross Profit"].sum()/df["Sales"].sum()*100, color=ACCENT, ls="--", lw=1.5, label="Overall Avg")
ax.legend(fontsize=9)
style_fig(fig, [ax]); save("03_division_margin.png")

# ── 4D: Product Profitability Leaderboard ─────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 7))
top = prod.sort_values("Total_Gross_Profit", ascending=True).tail(15)
cols = [PALETTE.get(d,"#999") for d in top["Division"]]
bars = ax.barh(top["Product Name"], top["Total_Gross_Profit"], color=cols, edgecolor="white")
for b in bars:
    ax.text(b.get_width()+10, b.get_y()+b.get_height()/2,
            f"${b.get_width():,.0f}", va="center", fontsize=8.5)
ax.set_xlabel("Total Gross Profit ($)")
ax.set_title("Product Gross Profit Leaderboard", fontweight="bold")
patches = [mpatches.Patch(color=v, label=k) for k,v in PALETTE.items()]
ax.legend(handles=patches, loc="lower right", fontsize=9)
style_fig(fig, [ax]); save("04_product_leaderboard.png")

# ── 4E: Gross Margin % per Product ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 7))
pm = prod.sort_values("Gross Margin %", ascending=True)
cols = [PALETTE.get(d,"#999") for d in pm["Division"]]
bars = ax.barh(pm["Product Name"], pm["Gross Margin %"], color=cols, edgecolor="white")
avg_margin = df["Gross Profit"].sum()/df["Sales"].sum()*100
ax.axvline(avg_margin, color=ACCENT, ls="--", lw=1.5, label=f"Avg {avg_margin:.1f}%")
for b in bars:
    ax.text(b.get_width()+0.3, b.get_y()+b.get_height()/2,
            f"{b.get_width():.1f}%", va="center", fontsize=8)
ax.set_xlabel("Gross Margin (%)")
ax.set_title("Gross Margin % by Product", fontweight="bold")
ax.legend(fontsize=9)
patches = [mpatches.Patch(color=v, label=k) for k,v in PALETTE.items()]
ax.legend(handles=patches + [mpatches.Patch(color=ACCENT, label=f"Avg {avg_margin:.1f}%")], fontsize=9)
style_fig(fig, [ax]); save("05_product_margin.png")

# ── 4F: Scatter — Sales vs Gross Profit (bubble = units) ─────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
for div_name, grp in prod.groupby("Division"):
    sc = ax.scatter(grp["Total_Sales"], grp["Total_Gross_Profit"],
                    s=grp["Total_Units"]/5, alpha=0.75,
                    color=PALETTE.get(div_name,"#999"), label=div_name, edgecolors="white", linewidth=0.5)
for _, row in prod.iterrows():
    ax.annotate(row["Product Name"].replace("Wonka Bar - ","").replace("Wonka Bar -",""),
                (row["Total_Sales"], row["Total_Gross_Profit"]),
                fontsize=7.5, ha="center", va="bottom")
ax.set_xlabel("Total Sales ($)")
ax.set_ylabel("Total Gross Profit ($)")
ax.set_title("Sales vs Gross Profit (bubble size = Units sold)", fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"${v:,.0f}"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"${v:,.0f}"))
ax.legend(title="Division")
style_fig(fig, [ax]); save("06_sales_vs_profit_scatter.png")

# ── 4G: Cost vs Sales Scatter (margin risk) ──────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
for div_name, grp in prod.groupby("Division"):
    ax.scatter(grp["Total_Cost"], grp["Total_Sales"],
               color=PALETTE.get(div_name,"#999"), label=div_name,
               s=70, edgecolors="white", linewidth=0.5, alpha=0.85)
max_val = max(prod["Total_Sales"].max(), prod["Total_Cost"].max())
ax.plot([0, max_val], [0, max_val], "k--", lw=1, alpha=0.4, label="Break-even")
for _, row in prod.iterrows():
    ax.annotate(row["Product Name"].replace("Wonka Bar - ","").replace("Wonka Bar -",""),
                (row["Total_Cost"], row["Total_Sales"]),
                fontsize=7.5, ha="center", va="bottom")
ax.set_xlabel("Total Cost ($)")
ax.set_ylabel("Total Sales ($)")
ax.set_title("Cost vs Sales — Margin Risk Diagnostics", fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"${v:,.0f}"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"${v:,.0f}"))
ax.legend(title="Division")
style_fig(fig, [ax]); save("07_cost_vs_sales.png")

# ── 4H: Pareto — Revenue ─────────────────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(12, 6))
p_rev = prod.sort_values("Total_Sales", ascending=False).reset_index(drop=True)
p_rev["Cumulative Rev %"] = p_rev["Total_Sales"].cumsum() / p_rev["Total_Sales"].sum() * 100
bars = ax1.bar(p_rev["Product Name"], p_rev["Total_Sales"],
               color=[PALETTE.get(d,"#999") for d in p_rev["Division"]], edgecolor="white")
ax1.set_ylabel("Total Sales ($)", color="black")
ax1.set_xticklabels(p_rev["Product Name"], rotation=45, ha="right", fontsize=9)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"${v:,.0f}"))
ax2 = ax1.twinx()
ax2.plot(p_rev["Product Name"], p_rev["Cumulative Rev %"], color=ACCENT, marker="o", ms=5, lw=2)
ax2.axhline(80, color="red", ls="--", lw=1, alpha=0.7)
ax2.set_ylabel("Cumulative Revenue %", color=ACCENT)
ax2.set_ylim(0, 110)
ax1.set_title("Pareto Analysis — Revenue Concentration", fontweight="bold")
patches = [mpatches.Patch(color=v, label=k) for k,v in PALETTE.items()]
ax1.legend(handles=patches, loc="upper right", fontsize=9)
style_fig(fig, [ax1, ax2]); save("08_pareto_revenue.png")

# ── 4I: Pareto — Profit ───────────────────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(12, 6))
p_prf = prod.sort_values("Total_Gross_Profit", ascending=False).reset_index(drop=True)
p_prf["Cumulative Prf %"] = p_prf["Total_Gross_Profit"].cumsum() / p_prf["Total_Gross_Profit"].sum() * 100
bars = ax1.bar(p_prf["Product Name"], p_prf["Total_Gross_Profit"],
               color=[PALETTE.get(d,"#999") for d in p_prf["Division"]], edgecolor="white")
ax1.set_ylabel("Total Gross Profit ($)")
ax1.set_xticklabels(p_prf["Product Name"], rotation=45, ha="right", fontsize=9)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"${v:,.0f}"))
ax2 = ax1.twinx()
ax2.plot(p_prf["Product Name"], p_prf["Cumulative Prf %"], color="#2E8B57", marker="o", ms=5, lw=2)
ax2.axhline(80, color="red", ls="--", lw=1, alpha=0.7)
ax2.set_ylabel("Cumulative Profit %", color="#2E8B57")
ax2.set_ylim(0, 110)
ax1.set_title("Pareto Analysis — Profit Concentration", fontweight="bold")
patches = [mpatches.Patch(color=v, label=k) for k,v in PALETTE.items()]
ax1.legend(handles=patches, loc="upper right", fontsize=9)
style_fig(fig, [ax1, ax2]); save("09_pareto_profit.png")

# ── 4J: Revenue Contribution Pie ──────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.pie(div["Revenue Contribution"], labels=div["Division"],
        colors=[PALETTE[d] for d in div["Division"]],
        autopct="%1.1f%%", startangle=140, pctdistance=0.75,
        wedgeprops={"edgecolor":"white","linewidth":1.5})
ax1.set_title("Revenue Share by Division", fontweight="bold")
ax2.pie(div["Profit Contribution"], labels=div["Division"],
        colors=[PALETTE[d] for d in div["Division"]],
        autopct="%1.1f%%", startangle=140, pctdistance=0.75,
        wedgeprops={"edgecolor":"white","linewidth":1.5})
ax2.set_title("Gross Profit Share by Division", fontweight="bold")
style_fig(fig); save("10_division_pie_charts.png")

# ── 4K: Monthly Revenue Trend ─────────────────────────────────────────────────
monthly = df.groupby(["Month","Division"])["Sales"].sum().reset_index()
monthly["Month_dt"] = monthly["Month"].dt.to_timestamp()
fig, ax = plt.subplots(figsize=(12, 5))
for div_name, grp in monthly.groupby("Division"):
    ax.plot(grp["Month_dt"], grp["Sales"], marker="o", ms=4,
            color=PALETTE.get(div_name,"#999"), label=div_name, lw=2)
ax.set_xlabel("Month")
ax.set_ylabel("Sales ($)")
ax.set_title("Monthly Revenue Trend by Division", fontweight="bold")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"${v:,.0f}"))
ax.legend(title="Division")
plt.xticks(rotation=30)
style_fig(fig, [ax]); save("11_monthly_trend.png")

# ── 4L: Monthly Gross Margin % Trend ─────────────────────────────────────────
monthly_m = df.groupby(["Month","Division"]).agg(S=("Sales","sum"), GP=("Gross Profit","sum")).reset_index()
monthly_m["Margin %"] = monthly_m["GP"] / monthly_m["S"] * 100
monthly_m["Month_dt"] = monthly_m["Month"].dt.to_timestamp()
fig, ax = plt.subplots(figsize=(12, 5))
for div_name, grp in monthly_m.groupby("Division"):
    ax.plot(grp["Month_dt"], grp["Margin %"], marker="o", ms=4,
            color=PALETTE.get(div_name,"#999"), label=div_name, lw=2)
ax.set_xlabel("Month")
ax.set_ylabel("Gross Margin (%)")
ax.set_title("Monthly Gross Margin % Trend by Division", fontweight="bold")
ax.legend(title="Division")
plt.xticks(rotation=30)
style_fig(fig, [ax]); save("12_monthly_margin_trend.png")

# ── 4M: Profit per Unit Heatmap ──────────────────────────────────────────────
ppu_pivot = df.groupby(["Division","Product Name"])["Profit per Unit"].mean().unstack(level=0)
fig, ax = plt.subplots(figsize=(9, 8))
sns.heatmap(ppu_pivot, annot=True, fmt=".2f", cmap="YlGn",
            linewidths=0.5, ax=ax, cbar_kws={"label":"Avg Profit/Unit ($)"})
ax.set_title("Profit per Unit Heatmap (Product × Division)", fontweight="bold")
ax.set_xlabel("Division"); ax.set_ylabel("Product")
plt.tight_layout(); save("13_profit_per_unit_heatmap.png")

# ── 4N: Region Revenue & Margin ───────────────────────────────────────────────
reg = df.groupby("Region").agg(Sales=("Sales","sum"), GP=("Gross Profit","sum")).reset_index()
reg["Margin %"] = reg["GP"]/reg["Sales"]*100
fig, ax1 = plt.subplots(figsize=(8, 5))
bars = ax1.bar(reg["Region"], reg["Sales"], color=ACCENT, alpha=0.8, label="Revenue")
ax2 = ax1.twinx()
ax2.plot(reg["Region"], reg["Margin %"], color="#E87C6C", marker="D", ms=8, lw=2, label="Margin %")
ax1.set_ylabel("Total Sales ($)")
ax2.set_ylabel("Gross Margin (%)", color="#E87C6C")
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"${v:,.0f}"))
ax1.set_title("Revenue & Gross Margin % by Region", fontweight="bold")
lines1, lbls1 = ax1.get_legend_handles_labels()
lines2, lbls2 = ax2.get_legend_handles_labels()
ax1.legend(lines1+lines2, lbls1+lbls2, loc="upper right")
style_fig(fig, [ax1, ax2]); save("14_region_revenue_margin.png")

# ── 4O: Ship Mode Analysis ────────────────────────────────────────────────────
ship = df.groupby("Ship Mode").agg(Orders=("Row ID","count"), Sales=("Sales","sum"),
                                    GP=("Gross Profit","sum")).reset_index()
ship["Margin %"] = ship["GP"]/ship["Sales"]*100
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].bar(ship["Ship Mode"], ship["Orders"], color=ACCENT, alpha=0.8)
axes[0].set_title("Orders by Ship Mode"); axes[0].set_ylabel("Order Count")
axes[0].tick_params(axis="x", rotation=20)
axes[1].bar(ship["Ship Mode"], ship["Margin %"], color="#2E8B57", alpha=0.8)
axes[1].set_title("Gross Margin % by Ship Mode"); axes[1].set_ylabel("Margin %")
axes[1].tick_params(axis="x", rotation=20)
style_fig(fig, axes); save("15_ship_mode.png")

# ══════════════════════════════════════════════════════════════════════════════
# 5.  PARETO METRICS (print)
# ══════════════════════════════════════════════════════════════════════════════
print("\n[5/7] Pareto Metrics …")

# how many products account for 80% of revenue
p_rev_sort = prod.sort_values("Total_Sales", ascending=False).reset_index(drop=True)
p_rev_sort["Cum Rev %"] = p_rev_sort["Total_Sales"].cumsum() / p_rev_sort["Total_Sales"].sum() * 100
n80_rev = (p_rev_sort["Cum Rev %"] <= 80).sum() + 1
print(f"  {n80_rev} products drive 80% of revenue")

p_prf_sort = prod.sort_values("Total_Gross_Profit", ascending=False).reset_index(drop=True)
p_prf_sort["Cum Prf %"] = p_prf_sort["Total_Gross_Profit"].cumsum() / p_prf_sort["Total_Gross_Profit"].sum() * 100
n80_prf = (p_prf_sort["Cum Prf %"] <= 80).sum() + 1
print(f"  {n80_prf} products drive 80% of profit")

# ══════════════════════════════════════════════════════════════════════════════
# 6.  MARGIN RISK FLAGS
# ══════════════════════════════════════════════════════════════════════════════
print("\n[6/7] Margin risk flags …")

avg_m = df["Gross Profit"].sum() / df["Sales"].sum() * 100
low_margin = prod[prod["Gross Margin %"] < avg_m * 0.9][["Product Name","Division","Gross Margin %","Total_Sales","Total_Gross_Profit"]]
print(f"\n  ⚠  Products with margin < 90% of average ({avg_m:.1f}%):")
print(low_margin.to_string(index=False))
low_margin.to_csv(os.path.join(OUT_DIR, "margin_risk_products.csv"), index=False)

# ══════════════════════════════════════════════════════════════════════════════
# 7.  EXECUTIVE SUMMARY (text file)
# ══════════════════════════════════════════════════════════════════════════════
print("\n[7/7] Writing executive summary …")

total_sales = df["Sales"].sum()
total_gp    = df["Gross Profit"].sum()
overall_margin = total_gp / total_sales * 100
top3_prod   = prod.head(3)["Product Name"].tolist()
bot3_prod   = prod.tail(3)["Product Name"].tolist()
best_div    = div.loc[div["Gross Margin %"].idxmax(), "Division"]
worst_div   = div.loc[div["Gross Margin %"].idxmin(), "Division"]

summary = f"""
═══════════════════════════════════════════════════════════════════
  NASSAU CANDY DISTRIBUTOR — EXECUTIVE SUMMARY
  Product Line Profitability & Margin Performance Analysis
═══════════════════════════════════════════════════════════════════

OVERVIEW
--------
  Total Revenue        : ${total_sales:>12,.2f}
  Total Gross Profit   : ${total_gp:>12,.2f}
  Overall Gross Margin : {overall_margin:.1f}%
  Products Analysed    : {prod.shape[0]}
  Orders Analysed      : {df['Row ID'].nunique():,}
  Date Range           : {df['Order Date'].min().date()} → {df['Order Date'].max().date()}

DIVISION PERFORMANCE
--------------------
{div[['Division','Total_Sales','Total_Gross_Profit','Gross Margin %','Revenue Contribution','Profit Contribution']].to_string(index=False)}

  Best Margin Division : {best_div}
  Weakest Margin Div.  : {worst_div}

TOP 3 PRODUCTS BY GROSS PROFIT
--------------------------------
{prod.head(3)[['Product Name','Division','Total_Sales','Total_Gross_Profit','Gross Margin %']].to_string(index=False)}

BOTTOM 3 PRODUCTS BY GROSS PROFIT
-----------------------------------
{prod.tail(3)[['Product Name','Division','Total_Sales','Total_Gross_Profit','Gross Margin %']].to_string(index=False)}

PARETO CONCENTRATION
--------------------
  {n80_rev} product(s) account for 80% of revenue
  {n80_prf} product(s) account for 80% of profit

MARGIN RISK PRODUCTS (below 90% of avg margin)
-----------------------------------------------
{low_margin.to_string(index=False) if not low_margin.empty else "  None identified."}

STRATEGIC RECOMMENDATIONS
--------------------------
  1. PROTECT high-margin leaders ({', '.join(top3_prod[:2])}) — allocate marketing budget here.
  2. INVESTIGATE {worst_div} division — review cost structure and pricing for margin improvement.
  3. RATIONALISE or REPRICE margin-risk products flagged above.
  4. PARETO focus: the top {n80_prf} SKUs generate 80% of profit — any supply disruption here
     is high risk; build resilience in sourcing and inventory.
  5. REGIONAL STRATEGY: target growth in regions with high margin but lower order volume.

═══════════════════════════════════════════════════════════════════
"""

with open(os.path.join(OUT_DIR, "executive_summary.txt"), "w") as f:
    f.write(summary)

print(summary)
print(f"\n✅  All outputs saved to:  {OUT_DIR}/")
print("   Charts:  01_kpi_cards.png … 15_ship_mode.png")
print("   CSVs:    product_summary.csv, division_summary.csv, margin_risk_products.csv")
print("   Text:    executive_summary.txt")
