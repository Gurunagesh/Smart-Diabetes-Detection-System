# ============================================================
# pages/2_risk_dashboard.py — Risk Dashboard
# ============================================================
# WHAT: Main results page showing:
#         - Ensemble risk score + level
#         - Dual model comparison + agreement score
#         - Risk DNA radar chart (5 axes)
#         - Clinical vs Lifestyle risk split
#         - SHAP feature importance chart
# ============================================================

import streamlit as st
import plotly.graph_objects as go
#import matplotlib.pyplot as plt
#import numpy as np
from modules.predictor import load_models, predict
from modules.explainer  import load_explainer, get_shap_values, plot_shap_bar, compute_domain_shap
from modules.utils      import compute_radar_scores
from config             import RISK_COLORS, RISK_ICONS
from config import THEMES
from modules.utils import get_theme_css

# Inherit theme from session state (set in app.py)
theme_name = st.session_state.get('theme_name', 'Dark')
theme      = THEMES[theme_name]
st.markdown(get_theme_css(theme), unsafe_allow_html=True)


# --- Guard: require form submission ---
if not st.session_state.get('data_submitted'):
    st.warning("⚠️ No patient data found. Please complete Page 1 first.")
    st.stop()

form_data = st.session_state['form_data']

# --- Load models and run prediction ---
with st.spinner("Running risk analysis..."):
    models  = load_models()
    results = predict(form_data, models)

    explainer   = load_explainer(models['xgb'])
    shap_dict   = get_shap_values(
        results['processed_input'], explainer,
        models['features']
    )
    domain_shap = compute_domain_shap(shap_dict)

# Store results for other pages
st.session_state['results']   = results
st.session_state['shap_dict'] = shap_dict
st.session_state['models']    = models

# Define fillcolor based on the theme
fillcolor = theme.get('accent_light', 'rgba(231, 76, 60, 0.25)')

# ── HEADER ────────────────────────────────────────────────
st.markdown("## 📊 Risk Dashboard")
st.markdown(
    "Your complete diabetes risk profile — "
    "model predictions, explainability, and risk breakdown."
)
st.markdown("<hr>", unsafe_allow_html=True)

# ── SECTION 1: Key Metrics Row ───────────────────────────
st.markdown(
    "<div class='section-header'>🎯 Overall Risk Assessment</div>",
    unsafe_allow_html=True
)

m1, m2, m3, m4, m5 = st.columns(5)

ens  = results['ensemble']
lr   = results['lr']
xgb  = results['xgb']
agr  = results['agreement']

risk_color = RISK_COLORS[ens['risk_level']]
risk_icon  = RISK_ICONS[ens['risk_level']]

with m1:
    st.markdown(f"""
    <div style='font-size:13px; color:{theme['text_muted']};'>
        <div style='font-size:32px; color:{risk_color}; font-weight:700;'>
            {risk_icon} {ens['risk_level']}
        </div>
        <div style='font-size:22px; font-weight:600; color:{theme['text_primary']};'>
            {ens['probability']*100:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    lr_color = RISK_COLORS[lr['risk_level']]
    st.markdown(f"""
    <div style='font-size:13px; color:{theme['text_muted']};'>
        <div style='font-size:20px; color:{lr_color}; font-weight:600;'>
            {RISK_ICONS[lr['risk_level']]} {lr['risk_level']}
        </div>
        <div style='font-size:18px; font-weight:500;'>
            {lr['probability']*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    xgb_color = RISK_COLORS[xgb['risk_level']]
    st.markdown(f"""
    <div style='font-size:13px; color:{theme['text_muted']};'>
        <div style='font-size:20px; color:{xgb_color}; font-weight:600;'>
            {RISK_ICONS[xgb['risk_level']]} {xgb['risk_level']}
        </div>
        <div style='font-size:18px; font-weight:500;'>
            {xgb['probability']*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    agr_score = agr['score'] * 100
    agr_color = '#2ecc71' if agr_score > 85 else '#f39c12' if agr_score > 60 else '#e74c3c'
    st.markdown(f"""
    <div style='font-size:13px; color:{agr_color};'>
        <div style='font-size:20px; color:{agr_color}; font-weight:600;'>
            {agr_score:.0f}%</div>
        <div style='font-size:12px; color:#7f8c8d;'>
            {agr['label']}</div>
    </div>
    """, unsafe_allow_html=True)

with m5:
    top_feat = shap_dict['df'].iloc[0]['Feature'].replace('_', ' ')
    top_pct  = shap_dict['df'].iloc[0]['Contribution_%']
    st.markdown(f"""
    <div style='font-size:13px; color:{theme['text_muted']};'>
        <div style='font-size:15px; font-weight:600; color:#2c3e50;'>
            {top_feat}</div>
        <div style='font-size:18px; color:{theme['accent']}; font-weight:600;'>
            {top_pct:.1f}% impact</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── SECTION 2: Risk DNA Radar + Domain Split ─────────────
st.markdown(
    "<div class='section-header'>🧬 Risk DNA Profile</div>",
    unsafe_allow_html=True
)

radar_col, domain_col = st.columns([1, 1])

with radar_col:
    radar_scores = compute_radar_scores(form_data)
    categories   = list(radar_scores.keys())
    values       = list(radar_scores.values())
    values_closed = values + [values[0]]  # Close the polygon
    categories_closed = categories + [categories[0]]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r          = values_closed,
        theta      = categories_closed,
        fill       = 'toself',
        fillcolor  = fillcolor,
        line       = dict(color='#e74c3c', width=2),
        name       = 'Your Risk Profile'
    ))
    # Add Indian average reference
    avg_values = [45, 40, 35, 20, 38]
    avg_closed = avg_values + [avg_values[0]]
    fig_radar.add_trace(go.Scatterpolar(
        r          = avg_closed,
        theta      = categories_closed,
        fill       = 'toself',
        fillcolor  = 'rgba(52, 152, 219, 0.15)',
        line       = dict(color='#3498db', width=2, dash='dot'),
        name       = 'Indian Population Average'
    ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(size=9),
                gridcolor='#ecf0f1'
            ),
            angularaxis=dict(tickfont=dict(size=11))
        ),
        showlegend=True,
        title=dict(text='Risk DNA — 5-Axis Profile<br>'
                        '<sup>vs Indian Population Average</sup>',
                   x=0.5),
        height=420,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(x=0.75, y=0.05)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with domain_col:
    st.markdown("**Clinical vs Lifestyle Risk Breakdown**")
    st.markdown(
        "<div class='info-box'>"
        "This split shows <b>where</b> your risk is coming from. "
        "Clinical risk needs medical intervention. "
        "Lifestyle risk can be reduced through behaviour change."
        "</div>",
        unsafe_allow_html=True
    )

    total_domain = sum(domain_shap.values()) or 1
    for domain, score in domain_shap.items():
        pct      = score / total_domain * 100
        d_color  = ('#e74c3c' if domain == 'Clinical'
                    else '#f39c12' if domain == 'Lifestyle'
                    else '#9b59b6')
        bar_pct  = int(pct)

        st.markdown(f"""
        <div style='margin-bottom:16px;'>
            <div style='display:flex; justify-content:space-between;
                        margin-bottom:4px;'>
                <span style='font-weight:600; color:{d_color};'>
                    {domain}</span>
                <span style='font-weight:600;'>{pct:.1f}%</span>
            </div>
            <div style='background:#ecf0f1; border-radius:6px;
                        height:12px; overflow:hidden;'>
                <div style='width:{bar_pct}%; background:{d_color};
                            height:100%; border-radius:6px;
                            transition: width 0.5s;'></div>
            </div>
            <div style='font-size:12px; color:#7f8c8d; margin-top:2px;'>
                SHAP contribution: {score:.3f}</div>
        </div>
        """, unsafe_allow_html=True)

    # Domain action guide
    max_domain = max(domain_shap, key=domain_shap.get)
    if max_domain == 'Clinical':
        st.markdown(
            "<div class='warning-box'>🏥 Your risk is primarily "
            "clinical — consult a physician for blood work "
            "review and medical management.</div>",
            unsafe_allow_html=True
        )
    elif max_domain == 'Lifestyle':
        st.markdown(
            "<div class='insight-box'>🏃 Your risk is primarily "
            "lifestyle-driven — targeted behavioural changes "
            "can significantly reduce your risk.</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div class='warning-box'>🫀 Comorbidities are your "
            "primary driver — managing existing conditions is "
            "the priority intervention.</div>",
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── SECTION 3: SHAP Feature Importance ───────────────────
st.markdown(
    "<div class='section-header'>"
    "🔍 SHAP Explainability — Why This Prediction?</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='info-box'>"
    "Each bar shows how much a feature <b>pushed the prediction "
    "toward (red) or away from (green)</b> diabetes. "
    "This is specific to <b>this patient</b> — not a global average."
    "</div>",
    unsafe_allow_html=True
)

shap_fig = plot_shap_bar(shap_dict, top_n=12)
st.pyplot(shap_fig, use_container_width=True)

# Top contributors in plain text
st.markdown("**Top risk-increasing factors for this patient:**")
top_pos = shap_dict['top_positive']
for _, row in top_pos.iterrows():
    st.markdown(
        f"- **{row['Feature'].replace('_',' ')}**: "
        f"+{row['SHAP_Value']:.4f} SHAP "
        f"({row['Contribution_%']:.1f}% of total risk)"
    )