import pandas as pd
import numpy as np
from prophet import Prophet
import warnings
import logging

warnings.filterwarnings('ignore')
logging.getLogger('prophet').setLevel(logging.ERROR)
logging.getLogger('cmdstanpy').setLevel(logging.ERROR)


def run_forecasts(sku_df: pd.DataFrame, sales_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fits a Prophet model per SKU on 2 years of daily sales.
    Returns (forecasts_df, inventory_metrics_df).
    """
    results = []
    forecasts = []

    for _, sku in sku_df.iterrows():
        sid = sku['sku_id']
        s = sales_df[sales_df['sku_id'] == sid].rename(columns={'date': 'ds', 'qty_sold': 'y'})

        m = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            interval_width=0.90
        )
        m.fit(s[['ds', 'y']])

        future = m.make_future_dataframe(periods=30)
        fc = m.predict(future)
        fc['sku_id'] = sid
        forecasts.append(fc[['ds', 'sku_id', 'yhat', 'yhat_lower', 'yhat_upper']])

        hist = fc[fc['ds'] <= s['ds'].max()]
        avg_daily = max(hist['yhat'].mean(), 0.1)
        std_daily = s['y'].std()

        lead = sku['lead_time_days']
        D = avg_daily * 365
        S = sku['order_cost_inr']
        H = sku['unit_price_inr'] * sku['holding_cost_pct'] / 100
        eoq = round(np.sqrt(2 * D * S / max(H, 1)))

        z = 1.65  # 95% service level
        safety_stock = round(z * std_daily * np.sqrt(lead))
        rop = round(avg_daily * lead + safety_stock)
        dos = round(sku['current_stock'] / avg_daily, 1) if avg_daily > 0 else 999

        future_fc = fc[fc['ds'] > s['ds'].max()]['yhat'].clip(lower=0)
        demand_30d = round(future_fc.sum())

        if sku['current_stock'] < rop:
            status = 'Critical'
        elif sku['current_stock'] < rop * 1.5:
            status = 'Watch'
        else:
            status = 'Healthy'

        po_qty = max(0, eoq) if sku['current_stock'] < rop else 0

        results.append({
            'sku_id': sid,
            'avg_daily_demand': round(avg_daily, 1),
            'std_daily_demand': round(std_daily, 1),
            'eoq': eoq,
            'safety_stock': safety_stock,
            'reorder_point': rop,
            'days_of_supply': dos,
            'forecast_30d_demand': demand_30d,
            'status': status,
            'po_qty_recommended': po_qty
        })
        print(f"  {sid} ({sku['sku_name']}) — {status}, DOS: {dos} days")

    fc_df = pd.concat(forecasts)
    inv_df = pd.DataFrame(results)
    return fc_df, inv_df


if __name__ == '__main__':
    sku_df = pd.read_csv('sku_master.csv')
    sales_df = pd.read_csv('sales_history.csv', parse_dates=['date'])
    print("Running forecasts for all SKUs...")
    fc_df, inv_df = run_forecasts(sku_df, sales_df)
    fc_df.to_csv('forecasts.csv', index=False)
    inv_df.to_csv('inventory_metrics.csv', index=False)
    print(f"\nSaved forecasts.csv and inventory_metrics.csv")
    print(f"Critical: {(inv_df['status']=='Critical').sum()} | Watch: {(inv_df['status']=='Watch').sum()} | Healthy: {(inv_df['status']=='Healthy').sum()}")
