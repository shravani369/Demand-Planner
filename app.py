import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os

st.set_page_config(
    page_title="Inventory Demand Planner",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 16px 20px;
        border: 1px solid #e9ecef;
    }
    .status-critical { color: #dc3545; font-weight: 600; }
    .status-watch    { color: #fd7e14; font-weight: 600; }
    .status-healthy  { color: #198754; font-weight: 600; }
    .block-container { padding-top: 1.5rem; }
    div[data-testid="metric-container"] { background: #f8f9fa; border-radius: 10px; padding: 12px; border: 1px solid #e9ecef; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    sku_df  = pd.read_csv('sku_master.csv')
    sales_df = pd.read_csv('sales_history.csv', parse_dates=['date'])
    fc_df   = pd.read_csv('forecasts.csv', parse_dates=['ds'])
    inv_df  = pd.read_csv('inventory_metrics.csv')
    merged  = sku_df.merge(inv_df, on='sku_id')
    return sku_df, sales_df, fc_df, inv_df, merged


sku_df, sales_df, fc_df, inv_df, merged = load_data()

STATUS_COLOR = {'Critical': '#dc3545', 'Watch': '#fd7e14', 'Healthy': '#198754'}
STATUS_BG    = {'Critical': '#fff5f5', 'Watch': '#fff8f0', 'Healthy': '#f0fff4'}


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📦 Inventory Demand Planner")
    st.markdown("---")

    cat_options = ['All'] + sorted(merged['category'].unique().tolist())
    selected_cat = st.selectbox("Filter by category", cat_options)

    filtered = merged if selected_cat == 'All' else merged[merged['category'] == selected_cat]
    sku_options = filtered['sku_id'] + ' — ' + filtered['sku_name']
    selected_label = st.selectbox("Select SKU for detail view", sku_options)
    selected_sku = selected_label.split(' — ')[0]

    st.markdown("---")
    st.markdown("**Service level**")
    service_level = st.selectbox("Target fill rate", ["95% (Z=1.65)", "99% (Z=2.33)", "90% (Z=1.28)"])
    z_map = {"95% (Z=1.65)": 1.65, "99% (Z=2.33)": 2.33, "90% (Z=1.28)": 1.28}
    z_val = z_map[service_level]

    st.markdown("---")
    st.caption("Data: 2023–2024 synthetic sales · Prophet forecast: +30 days")


# ── Page title ────────────────────────────────────────────────────────────────
st.title("📦 Smart Inventory & Demand Planner")
st.caption("50 SKUs · Prophet demand forecasting · EOQ-based reorder recommendations")
st.markdown("---")


# ── KPI row ───────────────────────────────────────────────────────────────────
total_skus      = len(merged)
critical_count  = (merged['status'] == 'Critical').sum()
watch_count     = (merged['status'] == 'Watch').sum()
healthy_count   = (merged['status'] == 'Healthy').sum()
total_po_value  = (merged['po_qty_recommended'] * merged['unit_price_inr']).sum()
avg_dos         = merged['days_of_supply'].replace(999, np.nan).mean()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total SKUs",       total_skus)
k2.metric("🔴 Critical",       critical_count,  delta=f"{round(critical_count/total_skus*100)}% of catalog", delta_color="inverse")
k3.metric("🟠 Watch",          watch_count)
k4.metric("🟢 Healthy",        healthy_count)
k5.metric("Avg Days of Supply", f"{avg_dos:.1f} days")
k6.metric("PO Value Pending",  f"₹{total_po_value:,.0f}")

st.markdown("---")


# ── TAB LAYOUT ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 SKU Forecast", "🚨 Stockout Risk", "🛒 PO Recommendations", "📈 Category Overview"])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: SKU FORECAST DETAIL
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    sku_info = merged[merged['sku_id'] == selected_sku].iloc[0]
    sku_fc   = fc_df[fc_df['sku_id'] == selected_sku]
    sku_hist = sales_df[sales_df['sku_id'] == selected_sku]

    hist_end = sku_hist['date'].max()
    fc_future = sku_fc[sku_fc['ds'] > hist_end]
    fc_hist   = sku_fc[sku_fc['ds'] <= hist_end]

    col_info, col_metrics = st.columns([1, 2])

    with col_info:
        status = sku_info['status']
        st.markdown(f"""
        <div style="background:{STATUS_BG[status]}; border-left:4px solid {STATUS_COLOR[status]};
                    border-radius:8px; padding:14px 16px; margin-bottom:12px;">
            <div style="font-size:18px; font-weight:600;">{sku_info['sku_name']}</div>
            <div style="color:#666; font-size:13px; margin:2px 0;">{sku_info['category']} · {sku_info['sku_id']}</div>
            <div style="margin-top:8px; font-size:13px;">Supplier: <b>{sku_info['supplier']}</b></div>
            <div style="font-size:13px;">Lead time: <b>{sku_info['lead_time_days']} days</b></div>
            <div style="margin-top:10px; font-size:16px; font-weight:600; color:{STATUS_COLOR[status]};">
                Status: {status}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_metrics:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current Stock",    f"{int(sku_info['current_stock'])} units")
        m2.metric("Reorder Point",    f"{int(sku_info['reorder_point'])} units")
        m3.metric("Days of Supply",   f"{sku_info['days_of_supply']} days")
        m4.metric("30-day Forecast",  f"{int(sku_info['forecast_30d_demand'])} units")
        m5, m6, m7, m8 = st.columns(4)
        m5.metric("EOQ",              f"{int(sku_info['eoq'])} units")
        m6.metric("Safety Stock",     f"{int(sku_info['safety_stock'])} units")
        m7.metric("Avg Daily Demand", f"{sku_info['avg_daily_demand']} units")
        m8.metric("Unit Price",       f"₹{sku_info['unit_price_inr']:,.0f}")

    # Demand forecast chart
    fig = make_subplots(specs=[[{"secondary_y": False}]])

    # Historical bars (last 90 days for readability)
    hist_90 = sku_hist[sku_hist['date'] >= hist_end - pd.Timedelta(days=90)]
    fig.add_trace(go.Bar(
        x=hist_90['date'], y=hist_90['qty_sold'],
        name='Actual sales', marker_color='#adb5bd', opacity=0.7
    ))

    # Prophet fitted line on history
    fc_hist_90 = fc_hist[fc_hist['ds'] >= hist_end - pd.Timedelta(days=90)]
    fig.add_trace(go.Scatter(
        x=fc_hist_90['ds'], y=fc_hist_90['yhat'].clip(lower=0),
        name='Model fit', line=dict(color='#4361ee', width=1.5, dash='dot')
    ))

    # Forecast + confidence band
    fig.add_trace(go.Scatter(
        x=fc_future['ds'],
        y=fc_future['yhat_upper'].clip(lower=0),
        fill=None, mode='lines', line=dict(width=0),
        showlegend=False, name='Upper CI'
    ))
    fig.add_trace(go.Scatter(
        x=fc_future['ds'],
        y=fc_future['yhat_lower'].clip(lower=0),
        fill='tonexty', mode='lines', line=dict(width=0),
        fillcolor='rgba(67,97,238,0.12)',
        name='90% confidence band'
    ))
    fig.add_trace(go.Scatter(
        x=fc_future['ds'], y=fc_future['yhat'].clip(lower=0),
        name='Forecast (30d)', line=dict(color='#4361ee', width=2.5)
    ))

    # Reorder point line
    fig.add_hline(
        y=sku_info['reorder_point'],
        line_dash='dash', line_color='#dc3545', line_width=1.5,
        annotation_text=f"Reorder Point ({int(sku_info['reorder_point'])})",
        annotation_position='top left'
    )

    # Current stock line
    fig.add_hline(
        y=sku_info['current_stock'],
        line_dash='dash', line_color='#198754', line_width=1.5,
        annotation_text=f"Current Stock ({int(sku_info['current_stock'])})",
        annotation_position='bottom right'
    )

    # Forecast divider
    fig.add_vline(x=str(hist_end), line_dash='dash', line_color='gray', line_width=1, opacity=0.5)
    fig.add_annotation(x=str(hist_end + pd.Timedelta(days=5)),
                       text="← History | Forecast →", showarrow=False,
                       font=dict(size=10, color='gray'), yref='paper', y=1.04)

    fig.update_layout(
        title=f"Demand forecast — {sku_info['sku_name']}",
        xaxis_title='Date', yaxis_title='Units sold/day',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
        height=420, margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor='#f0f0f0')
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📐 Formula breakdown for this SKU"):
        st.markdown(f"""
        | Formula | Value |
        |---------|-------|
        | Avg daily demand (D/365) | {sku_info['avg_daily_demand']} units/day |
        | Lead time | {int(sku_info['lead_time_days'])} days |
        | Order cost (S) | ₹{int(sku_info['order_cost_inr'])} per order |
        | Holding cost (H) | {sku_info['holding_cost_pct']}% of unit price = ₹{sku_info['unit_price_inr']*sku_info['holding_cost_pct']/100:.1f}/unit/yr |
        | **EOQ** = √(2DS/H) | **{int(sku_info['eoq'])} units** |
        | Safety Stock = Z × σ × √LT (Z={z_val}) | **{int(sku_info['safety_stock'])} units** |
        | **Reorder Point** = avg_daily × LT + SS | **{int(sku_info['reorder_point'])} units** |
        | Days of Supply = stock / avg_daily | **{sku_info['days_of_supply']} days** |
        """)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: STOCKOUT RISK TABLE
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Stockout risk tracker")
    st.caption("SKUs ranked by urgency — Critical means stock is below reorder point right now.")

    risk_df = merged.copy()
    risk_df['stock_gap'] = risk_df['current_stock'] - risk_df['reorder_point']
    risk_df = risk_df.sort_values(['status', 'days_of_supply'], ascending=[True, True])

    def status_badge(s):
        colors = {'Critical': '#dc3545', 'Watch': '#fd7e14', 'Healthy': '#198754'}
        return f'<span style="background:{colors[s]};color:white;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;">{s}</span>'

    display_cols = ['sku_id', 'sku_name', 'category', 'supplier', 'current_stock',
                    'reorder_point', 'days_of_supply', 'forecast_30d_demand', 'status', 'stock_gap']

    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        status_filter = st.multiselect("Filter by status", ['Critical', 'Watch', 'Healthy'],
                                       default=['Critical', 'Watch'])
    with col_f2:
        cat_filter = st.multiselect("Filter by category", merged['category'].unique().tolist(),
                                    default=merged['category'].unique().tolist())

    risk_filtered = risk_df[
        risk_df['status'].isin(status_filter) &
        risk_df['category'].isin(cat_filter)
    ][display_cols].copy()

    risk_filtered.columns = ['SKU ID', 'SKU Name', 'Category', 'Supplier', 'Stock',
                              'Reorder Point', 'Days of Supply', '30d Forecast', 'Status', 'Stock Gap']

    def color_status(val):
        colors = {'Critical': 'background-color:#fff5f5;color:#dc3545;font-weight:600',
                  'Watch':    'background-color:#fff8f0;color:#fd7e14;font-weight:600',
                  'Healthy':  'background-color:#f0fff4;color:#198754;font-weight:600'}
        return colors.get(val, '')

    def color_gap(val):
        if val < 0:
            return 'color:#dc3545; font-weight:600'
        return 'color:#198754'

    styled = risk_filtered.style\
        .map(color_status, subset=['Status'])\
        .map(color_gap, subset=['Stock Gap'])\
        .format({'Days of Supply': '{:.1f}', 'Stock Gap': '{:+d}'})

    st.dataframe(styled, use_container_width=True, height=500)

    # Bubble chart: DOS vs stock gap
    fig_bubble = px.scatter(
        merged, x='days_of_supply', y='stock_gap',
        color='status', size='forecast_30d_demand',
        hover_name='sku_name', hover_data=['category', 'supplier'],
        color_discrete_map=STATUS_COLOR,
        labels={'days_of_supply': 'Days of supply', 'stock_gap': 'Stock vs reorder point (units)'},
        title='Risk map — bubble size = 30-day forecast demand'
    )
    fig_bubble.add_hline(y=0, line_dash='dash', line_color='gray', opacity=0.5)
    fig_bubble.add_vline(x=7,  line_dash='dash', line_color='#fd7e14', opacity=0.5,
                         annotation_text='7-day threshold')
    fig_bubble.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig_bubble, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: PO RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Purchase order recommendations")
    st.caption("Auto-generated based on EOQ formula and current stock vs reorder point.")

    po_df = merged[merged['po_qty_recommended'] > 0].copy()
    po_df['po_value_inr'] = (po_df['po_qty_recommended'] * po_df['unit_price_inr']).round(0)
    po_df = po_df.sort_values('days_of_supply')

    if len(po_df) == 0:
        st.success("All SKUs are above reorder point — no POs needed right now!")
    else:
        # Summary by supplier
        st.markdown("##### PO summary by supplier")
        supplier_summary = po_df.groupby('supplier').agg(
            skus=('sku_id', 'count'),
            total_units=('po_qty_recommended', 'sum'),
            total_value=('po_value_inr', 'sum')
        ).reset_index().sort_values('total_value', ascending=False)
        supplier_summary['total_value'] = supplier_summary['total_value'].apply(lambda x: f"₹{x:,.0f}")

        col_s1, col_s2 = st.columns([1, 1])
        with col_s1:
            st.dataframe(supplier_summary, use_container_width=True, hide_index=True)
        with col_s2:
            fig_pie = px.pie(
                po_df.groupby('supplier')['po_value_inr'].sum().reset_index(),
                values='po_value_inr', names='supplier',
                title='PO value split by supplier',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_pie.update_layout(height=280, margin=dict(t=40, b=10))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("##### Full PO sheet")
        po_display = po_df[['sku_id', 'sku_name', 'category', 'supplier',
                             'current_stock', 'reorder_point', 'eoq',
                             'po_qty_recommended', 'unit_price_inr', 'po_value_inr',
                             'days_of_supply', 'lead_time_days']].copy()
        po_display.columns = ['SKU ID', 'SKU Name', 'Category', 'Supplier', 'Current Stock',
                               'Reorder Point', 'EOQ', 'Order Qty', 'Unit Price (₹)',
                               'PO Value (₹)', 'Days of Supply', 'Lead Time (days)']
        po_display = po_display.sort_values('Days of Supply')

        st.dataframe(po_display.style.format({
            'PO Value (₹)': '₹{:,.0f}',
            'Unit Price (₹)': '₹{:,.0f}',
            'Days of Supply': '{:.1f}'
        }), use_container_width=True, height=420)

        csv = po_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇ Download PO sheet as CSV",
            data=csv,
            file_name='purchase_order_recommendations.csv',
            mime='text/csv'
        )

        total_val = po_df['po_value_inr'].sum()
        st.info(f"Total PO value across **{len(po_df)} SKUs** from **{po_df['supplier'].nunique()} suppliers**: ₹{total_val:,.0f}")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: CATEGORY OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Category-level inventory health")

    cat_summary = merged.groupby('category').agg(
        total_skus=('sku_id', 'count'),
        critical=('status', lambda x: (x == 'Critical').sum()),
        watch=('status',    lambda x: (x == 'Watch').sum()),
        healthy=('status',  lambda x: (x == 'Healthy').sum()),
        avg_dos=('days_of_supply', lambda x: x.replace(999, np.nan).mean()),
        total_forecast_30d=('forecast_30d_demand', 'sum'),
        avg_turnover=('avg_daily_demand', 'mean')
    ).reset_index()

    # Stacked bar: status split per category
    fig_cat = go.Figure()
    fig_cat.add_trace(go.Bar(name='Healthy',  x=cat_summary['category'], y=cat_summary['healthy'],
                             marker_color='#198754'))
    fig_cat.add_trace(go.Bar(name='Watch',    x=cat_summary['category'], y=cat_summary['watch'],
                             marker_color='#fd7e14'))
    fig_cat.add_trace(go.Bar(name='Critical', x=cat_summary['category'], y=cat_summary['critical'],
                             marker_color='#dc3545'))
    fig_cat.update_layout(
        barmode='stack', title='SKU health by category',
        yaxis_title='Number of SKUs', height=350,
        plot_bgcolor='white', paper_bgcolor='white',
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig_cat, use_container_width=True)

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        fig_dos = px.bar(
            cat_summary.sort_values('avg_dos'),
            x='avg_dos', y='category', orientation='h',
            title='Avg days of supply by category',
            color='avg_dos',
            color_continuous_scale=['#dc3545', '#fd7e14', '#198754'],
            labels={'avg_dos': 'Avg days of supply', 'category': ''}
        )
        fig_dos.update_layout(height=300, plot_bgcolor='white', paper_bgcolor='white',
                              coloraxis_showscale=False)
        st.plotly_chart(fig_dos, use_container_width=True)

    with col_c2:
        fig_fc = px.bar(
            cat_summary.sort_values('total_forecast_30d', ascending=False),
            x='category', y='total_forecast_30d',
            title='Total 30-day demand forecast by category',
            color_discrete_sequence=['#4361ee'],
            labels={'total_forecast_30d': 'Forecasted units', 'category': ''}
        )
        fig_fc.update_layout(height=300, plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig_fc, use_container_width=True)

    # Heatmap: DOS per SKU within category
    st.markdown("##### Days of supply heatmap — all SKUs")
    heat_df = merged[['category', 'sku_name', 'days_of_supply']].copy()
    heat_df['days_of_supply'] = heat_df['days_of_supply'].replace(999, np.nan)
    heat_pivot = heat_df.pivot_table(index='sku_name', columns='category', values='days_of_supply')
    fig_heat = px.imshow(
        heat_pivot,
        color_continuous_scale=['#dc3545', '#fd7e14', '#fff5f0', '#d4edda', '#198754'],
        zmin=0, zmax=30,
        title='Days of supply per SKU (red = urgent, green = safe)',
        labels=dict(color='Days of Supply')
    )
    fig_heat.update_layout(height=600, margin=dict(l=160))
    st.plotly_chart(fig_heat, use_container_width=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Smart Inventory & Demand Planner · Prophet forecasting · EOQ-based replenishment · 95% service level · Data: 2023–2024 synthetic")
