# Smart Inventory & Demand Planner

End-to-end inventory analytics dashboard for 50 SKUs across 5 product categories — with Prophet-based demand forecasting, EOQ-driven reorder logic, and a live Streamlit dashboard.

## What it does

- Forecasts daily demand per SKU (next 30 days) using Facebook Prophet with weekly + yearly seasonality
- Computes EOQ, safety stock (95% service level), and reorder points using classical supply chain formulas
- Flags SKUs as Critical / Watch / Healthy based on current stock vs reorder point
- Generates purchase order recommendations grouped by supplier
- Exports PO sheet as CSV

## Formulas implemented

| Formula | Description |
|---------|-------------|
| EOQ = √(2DS/H) | Optimal order quantity |
| Safety Stock = Z × σ × √LT | Buffer for demand variability (Z=1.65 for 95%) |
| Reorder Point = avg_daily × LT + SS | Trigger point for replenishment |
| Days of Supply = stock / avg_daily | How many days until stockout |

## Setup

```bash
# 1. Clone and install dependencies
pip install -r requirements.txt

# 2. Generate synthetic data (50 SKUs, 2 years of sales history)
python data_gen.py

# 3. Run Prophet forecasts for all SKUs (takes ~2 minutes)
python forecast.py

# 4. Launch the dashboard
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → set `app.py` as the main file → Deploy

## Tech stack

- **Python** · pandas · numpy
- **Prophet** — time series forecasting with seasonality
- **Streamlit** — interactive dashboard
- **Plotly** — charts (bar, scatter, heatmap, pie)
- **Faker** — realistic synthetic data generation

## Project structure

```
inventory-planner/
├── data_gen.py          # Generates sku_master.csv + sales_history.csv
├── forecast.py          # Fits Prophet per SKU, outputs forecasts.csv + inventory_metrics.csv
├── app.py               # Streamlit dashboard (4 tabs)
├── requirements.txt
└── README.md
```

## Dashboard tabs

| Tab | What you see |
|-----|-------------|
| SKU Forecast | Demand chart with confidence bands, current stock vs ROP, all KPIs |
| Stockout Risk | Risk table + bubble chart, filterable by status/category |
| PO Recommendations | Auto-generated PO sheet by supplier, downloadable as CSV |
| Category Overview | Stacked bar, DOS by category, demand heatmap |
