import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Demand Planner | Bold Care",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* ── Global dark base ── */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
    [data-testid="block-container"], section[data-testid="stSidebar"] > div {
        background-color: #0a0a0f !important;
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #0f0f1a !important;
        border-right: 1px solid #1e2a4a !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }

    /* ── ALL text white on dark ── */
    p, span, div, label, h1, h2, h3, h4, h5, li, td, th {
        color: #e2e8f0 !important;
    }

    /* ── Metric cards ── */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #0f1729 0%, #111827 100%) !important;
        border: 1px solid #1e3a5f !important;
        border-radius: 12px !important;
        padding: 16px !important;
        box-shadow: 0 0 15px rgba(67,97,238,0.15) !important;
    }
    div[data-testid="metric-container"] > div { background: transparent !important; }
    div[data-testid="metric-container"] label,
    div[data-testid="metric-container"] [data-testid="stMetricLabel"] > div,
    div[data-testid="metric-container"] [data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"],
    div[data-testid="metric-container"] [data-testid="stMetricValue"] > div {
        color: #ffffff !important;
        font-size: 26px !important;
        font-weight: 700 !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricDelta"],
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] p {
        color: #ff6b6b !important;
        font-size: 11px !important;
    }

    /* ── Tabs ── */
    [data-testid="stTabs"] button { color: #475569 !important; font-weight: 500 !important; }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #4cc9f0 !important;
        border-bottom: 2px solid #4cc9f0 !important;
    }

    /* ── Selectbox & Multiselect — VISIBLE DROPDOWNS ── */
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stMultiSelect"] > div > div {
        background: #1a2035 !important;
        border: 1px solid #3a4a6b !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
    }
    /* Selected text in selectbox */
    [data-testid="stSelectbox"] > div > div > div,
    [data-testid="stMultiSelect"] > div > div > div {
        color: #e2e8f0 !important;
    }
    /* Dropdown arrow / icon */
    [data-testid="stSelectbox"] svg,
    [data-testid="stMultiSelect"] svg {
        fill: #94a3b8 !important;
    }
    /* Dropdown popup menu */
    [data-baseweb="popover"] ul,
    [data-baseweb="menu"] ul,
    [data-baseweb="select"] ul {
        background-color: #1a2035 !important;
        border: 1px solid #3a4a6b !important;
    }
    [data-baseweb="popover"] li,
    [data-baseweb="menu"] li {
        background-color: #1a2035 !important;
        color: #e2e8f0 !important;
    }
    [data-baseweb="popover"] li:hover,
    [data-baseweb="menu"] li:hover {
        background-color: #2a3a5f !important;
    }
    /* Multi-select tags */
    [data-baseweb="tag"] {
        background-color: #2a3a5f !important;
        color: #e2e8f0 !important;
    }
    [data-baseweb="tag"] span { color: #e2e8f0 !important; }

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] { border: 1px solid #1e2a4a !important; border-radius: 10px !important; }
    .dvn-scroller { background: #0f1729 !important; }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        background: #0f1729 !important;
        border: 1px solid #1e3a5f !important;
        border-radius: 10px !important;
    }
    [data-testid="stExpander"] summary p { color: #94a3b8 !important; }

    /* ── Download button ── */
    [data-testid="stDownloadButton"] button {
        background: linear-gradient(135deg, #4361ee, #3a0ca3) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 0 20px rgba(67,97,238,0.4) !important;
    }

    /* ── Markdown tables ── */
    table { border-collapse: collapse; width: 100%; }
    th { background: #1e3a5f !important; color: #e2e8f0 !important; padding: 8px 12px !important; }
    td { background: #0f1729 !important; color: #94a3b8 !important; padding: 6px 12px !important; border-bottom: 1px solid #1e2a4a !important; }

    /* ── Info / success boxes ── */
    [data-testid="stInfo"]    { background: #0f1729 !important; border: 1px solid #1e3a5f !important; color: #e2e8f0 !important; }
    [data-testid="stSuccess"] { background: #052e16 !important; border: 1px solid #065f46 !important; color: #34d399 !important; }

    /* ── Caption ── */
    [data-testid="stCaptionContainer"] p { color: #475569 !important; }

    hr { border-color: #1e2a4a !important; }

    /* ── Custom components ── */
    .glow-card {
        background: linear-gradient(135deg, #0f1729, #111827);
        border: 1px solid #1e3a5f;
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 14px;
        box-shadow: 0 0 20px rgba(67,97,238,0.08);
    }
    .neon-title {
        font-size: 30px !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #4361ee, #7b2ff7, #4cc9f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 !important;
    }
    .badge-critical { background:#2d0a0a; color:#ff6b6b !important; border:1px solid #7f1d1d; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:700; display:inline-block; }
    .badge-watch    { background:#2d1a00; color:#fbbf24 !important; border:1px solid #78350f; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:700; display:inline-block; }
    .badge-healthy  { background:#052e16; color:#34d399 !important; border:1px solid #065f46; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:700; display:inline-block; }
</style>
""", unsafe_allow_html=True)

STATUS_COLOR  = {'Critical': '#ff6b6b', 'Watch': '#fbbf24', 'Healthy': '#34d399'}
STATUS_BG     = {'Critical': '#2d0a0a', 'Watch': '#2d1a00',  'Healthy': '#052e16'}
STATUS_BORDER = {'Critical': '#7f1d1d', 'Watch': '#78350f',  'Healthy': '#065f46'}

CHART_DEFAULTS = dict(
    paper_bgcolor='#0a0a0f',
    plot_bgcolor='#0f1729',
    font=dict(color='#94a3b8', family='Inter, sans-serif'),
    margin=dict(l=40, r=40, t=50, b=40),
)

def dark_axes(fig):
    fig.update_xaxes(gridcolor='#1e2a4a', linecolor='#1e2a4a', tickcolor='#475569', tickfont=dict(color='#64748b'))
    fig.update_yaxes(gridcolor='#1e2a4a', linecolor='#1e2a4a', tickcolor='#475569', tickfont=dict(color='#64748b'))
    return fig

@st.cache_data
def load_data():
    sku_df   = pd.read_csv('sku_master.csv')
    sales_df = pd.read_csv('sales_history.csv', parse_dates=['date'])
    fc_df    = pd.read_csv('forecasts.csv', parse_dates=['ds'])
    inv_df   = pd.read_csv('inventory_metrics.csv')
    merged   = sku_df.merge(inv_df, on='sku_id')
    return sku_df, sales_df, fc_df, inv_df, merged

sku_df, sales_df, fc_df, inv_df, merged = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:10px 0 20px;">
        <div style="font-size:20px;font-weight:800;color:#4361ee;">📦 Demand Planner</div>
        <div style="font-size:11px;color:#475569;margin-top:2px;">Bold Care · Inventory Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    cat_options    = ['All'] + sorted(merged['category'].unique().tolist())
    selected_cat   = st.selectbox("Filter by category", cat_options)
    filtered       = merged if selected_cat == 'All' else merged[merged['category'] == selected_cat]
    sku_options    = filtered['sku_id'] + ' — ' + filtered['sku_name']
    selected_label = st.selectbox("Select SKU", sku_options)
    selected_sku   = selected_label.split(' — ')[0]

    st.markdown("---")
    service_level = st.selectbox("Service level", ["95% (Z=1.65)", "99% (Z=2.33)", "90% (Z=1.28)"])
    z_map = {"95% (Z=1.65)": 1.65, "99% (Z=2.33)": 2.33, "90% (Z=1.28)": 1.28}
    z_val = z_map[service_level]
    st.markdown("---")

    total_skus     = len(merged)
    critical_count = (merged['status'] == 'Critical').sum()
    watch_count    = (merged['status'] == 'Watch').sum()
    healthy_count  = (merged['status'] == 'Healthy').sum()

    st.markdown(f"""
    <div class="glow-card" style="padding:14px 16px;">
        <div style="font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;">Catalog Health</div>
        <div style="display:flex;flex-direction:column;gap:8px;">
            <span class="badge-critical">🔴 {critical_count} Critical</span>
            <span class="badge-watch">🟡 {watch_count} Watch</span>
            <span class="badge-healthy">🟢 {healthy_count} Healthy</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Prophet · EOQ · Safety Stock · 95% SL")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<p class="neon-title">Smart Inventory & Demand Planner</p>
<p style="color:#475569;font-size:13px;margin:4px 0 0;">
    50 SKUs · Prophet time-series forecasting · EOQ-based replenishment · Real-time stockout risk
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# ── KPI Row ───────────────────────────────────────────────────────────────────
total_po_value = (merged['po_qty_recommended'] * merged['unit_price_inr']).sum()
avg_dos        = merged['days_of_supply'].replace(999, np.nan).mean()

k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.metric("Total SKUs",         total_skus)
k2.metric("🔴 Critical",         critical_count, delta=f"{round(critical_count/total_skus*100)}% of catalog", delta_color="inverse")
k3.metric("🟡 Watch",            watch_count)
k4.metric("🟢 Healthy",          healthy_count)
k5.metric("Avg Days of Supply",  f"{avg_dos:.1f}d")
k6.metric("PO Value Pending",    f"₹{total_po_value/1e6:.2f}M")
st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5 = st.tabs([
    "📊 SKU Forecast","🚨 Stockout Risk","🛒 PO Recommendations",
    "📈 Category Overview","🔬 Analytics Deep Dive"
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — SKU FORECAST
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    sku_info  = merged[merged['sku_id'] == selected_sku].iloc[0]
    sku_fc    = fc_df[fc_df['sku_id'] == selected_sku]
    sku_hist  = sales_df[sales_df['sku_id'] == selected_sku]
    hist_end  = sku_hist['date'].max()
    fc_future = sku_fc[sku_fc['ds'] > hist_end]
    fc_hist_  = sku_fc[sku_fc['ds'] <= hist_end]
    status    = sku_info['status']

    col_info, col_metrics = st.columns([1, 2])
    with col_info:
        st.markdown(f"""
        <div class="glow-card" style="border-color:{STATUS_BORDER[status]};">
            <div style="font-size:20px;font-weight:700;color:#f1f5f9;">{sku_info['sku_name']}</div>
            <div style="color:#475569;font-size:12px;margin:3px 0 10px;">{sku_info['category']} · {sku_info['sku_id']}</div>
            <div style="font-size:12px;color:#64748b;margin-bottom:4px;">
                Supplier: <span style="color:#cbd5e1;font-weight:600;">{sku_info['supplier']}</span>
            </div>
            <div style="font-size:12px;color:#64748b;margin-bottom:12px;">
                Lead time: <span style="color:#cbd5e1;font-weight:600;">{sku_info['lead_time_days']} days</span>
            </div>
            <span class="badge-{status.lower()}">⬤ {status}</span>
        </div>
        """, unsafe_allow_html=True)

    with col_metrics:
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Current Stock",    f"{int(sku_info['current_stock'])} units")
        m2.metric("Reorder Point",    f"{int(sku_info['reorder_point'])} units")
        m3.metric("Days of Supply",   f"{sku_info['days_of_supply']}d")
        m4.metric("30d Forecast",     f"{int(sku_info['forecast_30d_demand'])} units")
        m5,m6,m7,m8 = st.columns(4)
        m5.metric("EOQ",              f"{int(sku_info['eoq'])} units")
        m6.metric("Safety Stock",     f"{int(sku_info['safety_stock'])} units")
        m7.metric("Avg Daily Demand", f"{sku_info['avg_daily_demand']}/day")
        m8.metric("Unit Price",       f"₹{sku_info['unit_price_inr']:,.0f}")

    # Forecast chart
    hist_90    = sku_hist[sku_hist['date'] >= hist_end - pd.Timedelta(days=90)]
    fc_hist_90 = fc_hist_[fc_hist_['ds'] >= hist_end - pd.Timedelta(days=90)]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=hist_90['date'], y=hist_90['qty_sold'],
                         name='Actual sales', marker_color='#1e3a5f', opacity=0.9))
    fig.add_trace(go.Scatter(x=fc_hist_90['ds'], y=fc_hist_90['yhat'].clip(lower=0),
                             name='Model fit', line=dict(color='#4361ee', width=1.5, dash='dot')))
    fig.add_trace(go.Scatter(x=fc_future['ds'], y=fc_future['yhat_upper'].clip(lower=0),
                             fill=None, mode='lines', line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=fc_future['ds'], y=fc_future['yhat_lower'].clip(lower=0),
                             fill='tonexty', mode='lines', line=dict(width=0),
                             fillcolor='rgba(67,97,238,0.18)', name='90% CI'))
    fig.add_trace(go.Scatter(x=fc_future['ds'], y=fc_future['yhat'].clip(lower=0),
                             name='Forecast (30d)', line=dict(color='#4cc9f0', width=2.5)))
    fig.add_hline(y=sku_info['reorder_point'], line_dash='dash', line_color='#ff6b6b', line_width=1.5,
                  annotation_text=f"ROP ({int(sku_info['reorder_point'])})",
                  annotation_font_color='#ff6b6b', annotation_position='top left')
    fig.add_hline(y=sku_info['current_stock'], line_dash='dash', line_color='#34d399', line_width=1.5,
                  annotation_text=f"Stock ({int(sku_info['current_stock'])})",
                  annotation_font_color='#34d399', annotation_position='bottom right')
    fig.add_vline(x=str(hist_end), line_dash='dash', line_color='#475569', line_width=1, opacity=0.6)
    fig.update_layout(
        title=dict(text=f"Demand forecast — {sku_info['sku_name']}", font=dict(color='#e2e8f0', size=15)),
        xaxis_title='Date', yaxis_title='Units / day', height=420,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0,
                    bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8')),
        **CHART_DEFAULTS
    )
    dark_axes(fig)
    st.plotly_chart(fig, use_container_width=True)

    # ── Gauge: white/silver monochrome palette ──
    dos_val = min(float(sku_info['days_of_supply']), 60)
    lt_days = float(sku_info['lead_time_days'])

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=dos_val,
        delta={'reference': lt_days, 'suffix': 'd vs LT',
               'font': {'color': '#cbd5e1', 'size': 13}},
        title={'text': "Days of Supply", 'font': {'color': '#94a3b8', 'size': 13}},
        number={'suffix': ' days', 'font': {'color': '#ffffff', 'size': 28}},
        gauge={
            'axis': {
                'range': [0, 60],
                'tickcolor': '#64748b',
                'tickfont': {'color': '#64748b'},
                'tickwidth': 1,
            },
            # Bar colour: white when healthy, light silver when watch, mid-grey when critical
            'bar': {'color': '#ffffff' if status == 'Healthy' else ('#b0bec5' if status == 'Watch' else '#78909c'),
                    'thickness': 0.55},
            'bgcolor': '#0f1729',
            'borderwidth': 1,
            'bordercolor': '#1e2a4a',
            'steps': [
                # danger zone  — very dark
                {'range': [0, lt_days],   'color': '#1a1a2e'},
                # caution zone — slightly lighter
                {'range': [lt_days, 20],  'color': '#16213e'},
                # safe zone    — slightly lighter still
                {'range': [20, 60],       'color': '#0f3460'},
            ],
            'threshold': {
                'line': {'color': '#e2e8f0', 'width': 2},
                'thickness': 0.75,
                'value': lt_days,
            }
        }
    ))
    fig_gauge.update_layout(
        paper_bgcolor='#0a0a0f',
        font=dict(color='#94a3b8'),
        height=230,
        margin=dict(l=20, r=20, t=30, b=10)
    )

    col_g1, col_g2 = st.columns([1, 2])
    with col_g1:
        st.plotly_chart(fig_gauge, use_container_width=True)
    with col_g2:
        with st.expander("📐 Formula breakdown", expanded=True):
            st.markdown(f"""
| Formula | Value |
|---|---|
| Avg daily demand | **{sku_info['avg_daily_demand']} units/day** |
| Lead time | **{int(sku_info['lead_time_days'])} days** |
| EOQ = √(2DS/H) | **{int(sku_info['eoq'])} units** |
| Safety Stock = Z×σ×√LT (Z={z_val}) | **{int(sku_info['safety_stock'])} units** |
| Reorder Point = avg×LT + SS | **{int(sku_info['reorder_point'])} units** |
| Days of Supply = stock / avg | **{sku_info['days_of_supply']} days** |
            """)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — STOCKOUT RISK
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🚨 Stockout Risk Tracker")
    st.caption("SKUs ranked by urgency. Critical = stock already below reorder point.")

    risk_df = merged.copy()
    risk_df['stock_gap'] = risk_df['current_stock'] - risk_df['reorder_point']
    risk_df = risk_df.sort_values(['status','days_of_supply'], ascending=[True,True])

    all_categories = merged['category'].unique().tolist()

    col_f1,col_f2 = st.columns(2)
    with col_f1:
        status_filter = st.multiselect(
            "Status",
            ['Critical','Watch','Healthy'],
            default=['Critical','Watch']
        )
    with col_f2:
        cat_filter = st.multiselect(
            "Category",
            all_categories,
            default=all_categories   # FIX: always default to all so table is never empty
        )

    # Guard: if user clears all selections, fall back to showing everything
    active_statuses = status_filter if status_filter else ['Critical','Watch','Healthy']
    active_cats     = cat_filter     if cat_filter     else all_categories

    display_cols = ['sku_id','sku_name','category','supplier','current_stock',
                    'reorder_point','days_of_supply','forecast_30d_demand','status','stock_gap']
    risk_filtered = risk_df[
        risk_df['status'].isin(active_statuses) &
        risk_df['category'].isin(active_cats)
    ][display_cols].copy()
    risk_filtered.columns = ['SKU ID','SKU Name','Category','Supplier','Stock',
                              'Reorder Point','Days of Supply','30d Forecast','Status','Stock Gap']

    def color_status(val):
        m = {'Critical':'background-color:#2d0a0a;color:#ff6b6b;font-weight:700',
             'Watch':   'background-color:#2d1a00;color:#fbbf24;font-weight:700',
             'Healthy': 'background-color:#052e16;color:#34d399;font-weight:700'}
        return m.get(val,'')
    def color_gap(val):
        return 'color:#ff6b6b;font-weight:700' if val < 0 else 'color:#34d399'

    styled = risk_filtered.style\
        .map(color_status, subset=['Status'])\
        .map(color_gap, subset=['Stock Gap'])\
        .format({'Days of Supply':'{:.1f}','Stock Gap':'{:+d}'})
    st.dataframe(styled, use_container_width=True, height=420)

    fig_bubble = px.scatter(
        risk_df, x='days_of_supply', y='stock_gap',
        color='status', size='forecast_30d_demand',
        hover_name='sku_name', hover_data=['category','supplier'],
        color_discrete_map=STATUS_COLOR,
        labels={'days_of_supply':'Days of supply','stock_gap':'Stock vs ROP (units)'},
        title='Risk map — bubble size = 30-day forecast demand'
    )
    fig_bubble.add_hline(y=0, line_dash='dash', line_color='#475569', opacity=0.7)
    fig_bubble.add_vline(x=7, line_dash='dash', line_color='#fbbf24', opacity=0.6,
                         annotation_text='7-day threshold', annotation_font_color='#fbbf24')
    fig_bubble.update_layout(height=420, title_font_color='#e2e8f0', **CHART_DEFAULTS)
    dark_axes(fig_bubble)
    st.plotly_chart(fig_bubble, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — PO RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### 🛒 Purchase Order Recommendations")
    po_df = merged[merged['po_qty_recommended'] > 0].copy()
    po_df['po_value_inr'] = (po_df['po_qty_recommended'] * po_df['unit_price_inr']).round(0)
    po_df = po_df.sort_values('days_of_supply')

    # ── helper: render a plain HTML table with dark theme ──
    def html_table(df, col_formats=None):
        """Render df as a styled HTML table that always shows on dark backgrounds."""
        col_formats = col_formats or {}
        header_cells = ''.join(f'<th>{c}</th>' for c in df.columns)
        rows_html = ''
        for _, row in df.iterrows():
            cells = ''
            for col in df.columns:
                val = row[col]
                fmt = col_formats.get(col)
                display = fmt(val) if fmt else str(val)

                # colour rules
                style = 'color:#e2e8f0;'
                if col == 'Status':
                    if val == 'Critical': style = 'color:#ff6b6b;font-weight:700;'
                    elif val == 'Watch':  style = 'color:#fbbf24;font-weight:700;'
                    else:                 style = 'color:#34d399;font-weight:700;'
                elif col == 'DOS':
                    try:
                        v = float(val) if not isinstance(val, str) else float(val.replace('d',''))
                        style = 'color:#ff6b6b;' if v < 7 else ('color:#fbbf24;' if v < 14 else 'color:#34d399;')
                    except: pass
                elif col == 'Stock Gap':
                    try:
                        style = 'color:#ff6b6b;font-weight:700;' if float(val) < 0 else 'color:#34d399;'
                    except: pass

                cells += f'<td style="{style}padding:8px 12px;border-bottom:1px solid #1e2a4a;white-space:nowrap;">{display}</td>'
            rows_html += f'<tr style="background:#0f1729;">{cells}</tr>'

        return f"""
        <div style="overflow-x:auto;border:1px solid #1e2a4a;border-radius:10px;margin-bottom:16px;">
        <table style="border-collapse:collapse;width:100%;font-size:12px;font-family:Inter,sans-serif;">
            <thead>
                <tr style="background:#1e3a5f;">
                    {header_cells}
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        </div>
        """

    if len(po_df) == 0:
        st.success("All SKUs above reorder point — no POs needed!")
    else:
        total_val   = po_df['po_value_inr'].sum()
        total_units = po_df['po_qty_recommended'].sum()

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("SKUs needing PO",    len(po_df))
        c2.metric("Suppliers involved", po_df['supplier'].nunique())
        c3.metric("Total units to order", f"{int(total_units):,}")
        c4.metric("Total PO value",     f"₹{total_val/1e6:.2f}M")
        st.markdown("---")

        # ── Row 1: Supplier summary table + PO value by supplier pie ──
        col_s1, col_s2 = st.columns(2)

        sup_sum = po_df.groupby('supplier').agg(
            SKUs=('sku_id','count'),
            Units=('po_qty_recommended','sum'),
            Value=('po_value_inr','sum')
        ).reset_index().sort_values('Value', ascending=False)

        with col_s1:
            st.markdown("##### 📋 Supplier Summary")
            sup_display = sup_sum.copy()
            sup_display['Value'] = sup_display['Value'].apply(lambda x: f"₹{x:,.0f}")
            sup_display['Units'] = sup_display['Units'].apply(lambda x: f"{int(x):,}")
            st.markdown(html_table(sup_display), unsafe_allow_html=True)

        with col_s2:
            fig_pie1 = px.pie(
                sup_sum, values='Value', names='supplier',
                title='PO value split by supplier',
                color_discrete_sequence=['#4361ee','#7b2ff7','#4cc9f0','#f72585','#34d399'],
                hole=0.35,
            )
            fig_pie1.update_traces(
                textfont_color='white', textfont_size=11,
                textinfo='percent+label',
            )
            fig_pie1.update_layout(
                height=300, title_font_color='#e2e8f0',
                paper_bgcolor='#0a0a0f', font=dict(color='#94a3b8'),
                margin=dict(t=45,b=10,l=10,r=10),
                showlegend=False,
            )
            st.plotly_chart(fig_pie1, use_container_width=True)

        st.markdown("---")

        # ── Row 2: Category pie + Status pie ──
        col_p1, col_p2 = st.columns(2)

        cat_sum = po_df.groupby('category')['po_value_inr'].sum().reset_index()
        with col_p1:
            fig_pie2 = px.pie(
                cat_sum, values='po_value_inr', names='category',
                title='PO value split by category',
                color_discrete_sequence=['#4cc9f0','#f72585','#34d399','#fbbf24','#7b2ff7'],
                hole=0.35,
            )
            fig_pie2.update_traces(textfont_color='white', textfont_size=11, textinfo='percent+label')
            fig_pie2.update_layout(
                height=300, title_font_color='#e2e8f0',
                paper_bgcolor='#0a0a0f', font=dict(color='#94a3b8'),
                margin=dict(t=45,b=10,l=10,r=10), showlegend=False,
            )
            st.plotly_chart(fig_pie2, use_container_width=True)

        status_sum = po_df.groupby('status')['po_value_inr'].sum().reset_index()
        with col_p2:
            fig_pie3 = px.pie(
                status_sum, values='po_value_inr', names='status',
                title='PO value split by urgency',
                color_discrete_map=STATUS_COLOR,
                hole=0.35,
            )
            fig_pie3.update_traces(textfont_color='white', textfont_size=11, textinfo='percent+label')
            fig_pie3.update_layout(
                height=300, title_font_color='#e2e8f0',
                paper_bgcolor='#0a0a0f', font=dict(color='#94a3b8'),
                margin=dict(t=45,b=10,l=10,r=10), showlegend=False,
            )
            st.plotly_chart(fig_pie3, use_container_width=True)

        st.markdown("---")

        # ── Top 15 horizontal bar chart ──
        top_po = po_df.nlargest(15,'po_value_inr')
        fig_bar = px.bar(
            top_po, x='po_value_inr', y='sku_name', orientation='h',
            color='days_of_supply',
            color_continuous_scale=['#ff6b6b','#fbbf24','#34d399'],
            title='Top 15 SKUs by PO value  (colour = days of supply)',
            labels={'po_value_inr':'PO Value (₹)','sku_name':''},
        )
        fig_bar.update_layout(
            height=460, title_font_color='#e2e8f0',
            coloraxis_colorbar=dict(
                tickfont=dict(color='#94a3b8'),
                title=dict(text='DOS', font=dict(color='#94a3b8'))
            ),
            **CHART_DEFAULTS
        )
        dark_axes(fig_bar)
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")

        # ── Full PO detail table as HTML ──
        st.markdown("##### 📄 Full PO Detail")
        po_display = po_df[['sku_id','sku_name','category','supplier','current_stock',
                             'reorder_point','eoq','po_qty_recommended','unit_price_inr',
                             'po_value_inr','days_of_supply','lead_time_days','status']].copy()
        po_display.columns = ['SKU ID','SKU Name','Category','Supplier','Stock','ROP','EOQ',
                               'Order Qty','Unit Price (₹)','PO Value (₹)','DOS','Lead Time','Status']

        fmts = {
            'PO Value (₹)': lambda v: f"₹{v:,.0f}",
            'Unit Price (₹)': lambda v: f"₹{v:,.0f}",
            'DOS': lambda v: f"{v:.1f}d",
            'Stock': lambda v: f"{int(v):,}",
            'ROP': lambda v: f"{int(v):,}",
            'EOQ': lambda v: f"{int(v):,}",
            'Order Qty': lambda v: f"{int(v):,}",
        }
        st.markdown(html_table(po_display, col_formats=fmts), unsafe_allow_html=True)

        csv = po_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇ Download PO sheet as CSV", data=csv,
            file_name='purchase_order_recommendations.csv', mime='text/csv'
        )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — CATEGORY OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("### 📈 Category-level Inventory Health")
    cat_summary = merged.groupby('category').agg(
        total_skus=('sku_id','count'),
        critical=('status', lambda x:(x=='Critical').sum()),
        watch=('status',    lambda x:(x=='Watch').sum()),
        healthy=('status',  lambda x:(x=='Healthy').sum()),
        avg_dos=('days_of_supply', lambda x:x.replace(999,np.nan).mean()),
        total_forecast_30d=('forecast_30d_demand','sum'),
    ).reset_index()

    fig_cat = go.Figure()
    fig_cat.add_trace(go.Bar(name='Healthy',  x=cat_summary['category'], y=cat_summary['healthy'],  marker_color='#34d399'))
    fig_cat.add_trace(go.Bar(name='Watch',    x=cat_summary['category'], y=cat_summary['watch'],    marker_color='#fbbf24'))
    fig_cat.add_trace(go.Bar(name='Critical', x=cat_summary['category'], y=cat_summary['critical'], marker_color='#ff6b6b'))
    fig_cat.update_layout(barmode='stack',
                          title=dict(text='SKU health by category', font=dict(color='#e2e8f0')),
                          yaxis_title='SKUs', height=320,
                          legend=dict(orientation='h', yanchor='bottom', y=1.02,
                                      bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8')),
                          **CHART_DEFAULTS)
    dark_axes(fig_cat)
    st.plotly_chart(fig_cat, use_container_width=True)

    col_c1,col_c2 = st.columns(2)
    with col_c1:
        fig_dos = px.bar(cat_summary.sort_values('avg_dos'), x='avg_dos', y='category', orientation='h',
                         color='avg_dos', color_continuous_scale=['#ff6b6b','#fbbf24','#34d399'],
                         title='Avg days of supply', labels={'avg_dos':'Days','category':''})
        fig_dos.update_layout(height=300, title_font_color='#e2e8f0', coloraxis_showscale=False, **CHART_DEFAULTS)
        dark_axes(fig_dos)
        st.plotly_chart(fig_dos, use_container_width=True)
    with col_c2:
        fig_fc = px.bar(cat_summary.sort_values('total_forecast_30d', ascending=False),
                        x='category', y='total_forecast_30d',
                        color='total_forecast_30d', color_continuous_scale=['#4361ee','#4cc9f0'],
                        title='30-day demand forecast', labels={'total_forecast_30d':'Units','category':''})
        fig_fc.update_layout(height=300, title_font_color='#e2e8f0', coloraxis_showscale=False, **CHART_DEFAULTS)
        dark_axes(fig_fc)
        st.plotly_chart(fig_fc, use_container_width=True)

    # ── Heatmap fix: use all SKUs across all categories, fill NaN nicely ──
    heat_df = merged[['category','sku_name','days_of_supply']].copy()
    heat_df['days_of_supply'] = heat_df['days_of_supply'].replace(999, np.nan)

    # Build a complete grid so every SKU × every category has a cell
    all_cats  = sorted(heat_df['category'].unique())
    all_skus  = sorted(heat_df['sku_name'].unique())
    heat_pivot = heat_df.pivot_table(
        index='sku_name', columns='category',
        values='days_of_supply', aggfunc='mean'
    ).reindex(index=all_skus, columns=all_cats)

    fig_heat = px.imshow(
        heat_pivot,
        color_continuous_scale=['#ff6b6b','#fbbf24','#1e3a5f','#065f46','#34d399'],
        zmin=0, zmax=30,
        title='Days of supply heatmap — all SKUs',
        labels=dict(color='DOS'),
        aspect='auto',          # don't force square cells — fill the width properly
    )
    fig_heat.update_traces(
        xgap=2, ygap=2,        # small gaps so individual cells are visible
        hoverongaps=False,
    )
    fig_heat.update_layout(
        height=700,
        title_font_color='#e2e8f0',
        margin=dict(l=180, r=60, t=60, b=60),
        paper_bgcolor='#0a0a0f',
        font=dict(color='#94a3b8'),
        coloraxis_colorbar=dict(
            tickfont=dict(color='#94a3b8'),
            title=dict(text='DOS', font=dict(color='#94a3b8'))
        ),
        xaxis=dict(
            tickfont=dict(color='#94a3b8', size=11),
            title=dict(text='Category', font=dict(color='#64748b'))
        ),
        yaxis=dict(
            tickfont=dict(color='#94a3b8', size=9),
            title=dict(text='', font=dict(color='#64748b'))
        ),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — ANALYTICS DEEP DIVE
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown("### 🔬 Analytics Deep Dive")

    col_d1,col_d2 = st.columns(2)
    with col_d1:
        fig_eoq = px.scatter(merged, x='avg_daily_demand', y='eoq',
                             color='category', size='unit_price_inr', hover_name='sku_name',
                             color_discrete_sequence=['#4361ee','#7b2ff7','#4cc9f0','#f72585','#34d399'],
                             title='EOQ vs Avg Daily Demand',
                             labels={'avg_daily_demand':'Avg daily demand','eoq':'EOQ (units)'})
        fig_eoq.update_layout(height=380, title_font_color='#e2e8f0', **CHART_DEFAULTS)
        dark_axes(fig_eoq)
        st.plotly_chart(fig_eoq, use_container_width=True)
    with col_d2:
        fig_ss = px.scatter(merged, x='lead_time_days', y='safety_stock',
                            color='status', size='avg_daily_demand', hover_name='sku_name',
                            color_discrete_map=STATUS_COLOR,
                            title='Safety Stock vs Lead Time',
                            labels={'lead_time_days':'Lead time (days)','safety_stock':'Safety stock (units)'})
        fig_ss.update_layout(height=380, title_font_color='#e2e8f0', **CHART_DEFAULTS)
        dark_axes(fig_ss)
        st.plotly_chart(fig_ss, use_container_width=True)

    st.markdown("#### 💸 Inventory value at risk — Critical SKUs")
    critical_df = merged[merged['status']=='Critical'].copy()
    critical_df['value_at_risk'] = critical_df['reorder_point'] * critical_df['unit_price_inr']
    critical_df = critical_df.sort_values('value_at_risk', ascending=False).head(20)
    fig_risk = px.bar(critical_df, x='sku_name', y='value_at_risk',
                      color='days_of_supply', color_continuous_scale=['#ff6b6b','#fbbf24'],
                      title='Top 20 Critical SKUs by inventory value at risk',
                      labels={'value_at_risk':'Value at risk (₹)','sku_name':''})
    fig_risk.update_layout(height=380, title_font_color='#e2e8f0', xaxis_tickangle=-35,
                           coloraxis_colorbar=dict(tickfont=dict(color='#94a3b8'),
                                                   title=dict(text='DOS',font=dict(color='#94a3b8'))),
                           **CHART_DEFAULTS)
    dark_axes(fig_risk)
    st.plotly_chart(fig_risk, use_container_width=True)

    col_d3,col_d4 = st.columns(2)
    with col_d3:
        dos_clean = merged['days_of_supply'].replace(999, np.nan).dropna()
        fig_hist = px.histogram(dos_clean, nbins=30, title='Distribution of Days of Supply',
                                labels={'value':'Days of supply'}, color_discrete_sequence=['#4361ee'])
        fig_hist.add_vline(x=dos_clean.mean(), line_dash='dash', line_color='#4cc9f0',
                           annotation_text=f'Mean: {dos_clean.mean():.1f}d',
                           annotation_font_color='#4cc9f0')
        fig_hist.update_layout(height=320, title_font_color='#e2e8f0', showlegend=False, **CHART_DEFAULTS)
        dark_axes(fig_hist)
        st.plotly_chart(fig_hist, use_container_width=True)
    with col_d4:
        fig_box = px.box(merged, x='category', y='avg_daily_demand', color='category',
                         color_discrete_sequence=['#4361ee','#7b2ff7','#4cc9f0','#f72585','#34d399'],
                         title='Daily demand distribution by category',
                         labels={'avg_daily_demand':'Avg daily demand','category':''})
        fig_box.update_layout(height=320, title_font_color='#e2e8f0', showlegend=False, **CHART_DEFAULTS)
        dark_axes(fig_box)
        st.plotly_chart(fig_box, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#1e3a5f;font-size:12px;padding:8px 0;">
    Smart Inventory & Demand Planner · Prophet forecasting · EOQ replenishment · 95% service level · Bold Care 2025
</div>
""", unsafe_allow_html=True)
