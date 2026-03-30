# ============================================================
# pages/3_simulator.py — What-if Simulator
# ============================================================
# WHAT: Interactive risk simulation — two modes:
#   1. Manual what-if: user adjusts any feature, sees live
#      risk change
#   2. Recovery simulation: automatic 3-month projection
#      based on realistic lifestyle improvements
# WHY:  Static prediction tells you where you are.
#       Simulation tells you where you could be.
#       This is the feature that makes the app a
#       decision support tool, not just a calculator.
# ============================================================

import streamlit as st
import plotly.graph_objects as go
import numpy as np

from modules.predictor   import load_models, predict
from modules.recommender import simulate_recovery
from config              import RISK_COLORS, RISK_ICONS, CATEGORICAL_OPTIONS

st.set_page_config(
    page_title="What-if Simulator — DiabetesIQ",
    page_icon="🔮", layout="wide"
)

if not st.session_state.get('data_submitted'):
    st.warning("⚠️ No patient data found. Please complete Page 1 first.")
    st.stop()

form_data = st.session_state['form_data']
models    = load_models()
original  = st.session_state.get('results', predict(form_data, models))
orig_prob = original['ensemble']['probability']

st.markdown("## 🔮 What-if Risk Simulator")
st.markdown(
    "Adjust any input below and see how your risk changes "
    "instantly. Use the Recovery Simulation tab to see your "
    "projected risk after 90 days of lifestyle changes."
)
st.markdown("<hr>", unsafe_allow_html=True)

tab1, tab2 = st.tabs([
    "🎛️ Manual What-if Explorer",
    "📈 90-Day Recovery Simulation"
])

# ── TAB 1: Manual What-if ─────────────────────────────────
with tab1:
    st.markdown(
        "<div class='info-box'>"
        "Adjust the sliders and dropdowns. Risk updates "
        "automatically. Compare against your original risk "
        "shown in the baseline column.</div>",
        unsafe_allow_html=True
    )

    sim_col, result_col = st.columns([1.2, 1])

    with sim_col:
        st.markdown("**Adjust Clinical Values:**")
        cc1, cc2 = st.columns(2)
        with cc1:
            sim_hba1c = st.slider(
                "HbA1c (%)",
                min_value=4.0, max_value=14.0,
                value=float(form_data['HBA1C']),
                step=0.1,
                help="WHO diagnostic threshold: 6.5%"
            )
            sim_fbs = st.slider(
                "Fasting Blood Sugar (mg/dL)",
                min_value=60, max_value=300,
                value=int(form_data['Fasting_Blood_Sugar']),
                step=1
            )
        with cc2:
            sim_bmi = st.slider(
                "BMI (kg/m²)",
                min_value=14.0, max_value=45.0,
                value=float(form_data['BMI']),
                step=0.1
            )
            sim_ppbs = st.slider(
                "Postprandial BS (mg/dL)",
                min_value=80, max_value=400,
                value=int(form_data['Postprandial_Blood_Sugar']),
                step=1
            )

        st.markdown("**Adjust Lifestyle Factors:**")
        lc1, lc2, lc3 = st.columns(3)
        with lc1:
            sim_activity = st.selectbox(
                "Physical Activity",
                CATEGORICAL_OPTIONS['Physical_Activity'],
                index=CATEGORICAL_OPTIONS['Physical_Activity'].index(
                    form_data['Physical_Activity']
                )
            )
        with lc2:
            sim_stress = st.selectbox(
                "Stress Level",
                CATEGORICAL_OPTIONS['Stress_Level'],
                index=CATEGORICAL_OPTIONS['Stress_Level'].index(
                    form_data['Stress_Level']
                )
            )
        with lc3:
            sim_smoking = st.selectbox(
                "Smoking Status",
                CATEGORICAL_OPTIONS['Smoking_Status'],
                index=CATEGORICAL_OPTIONS['Smoking_Status'].index(
                    form_data['Smoking_Status']
                )
            )

    # Build simulated input and predict
    sim_data = form_data.copy()
    sim_data.update({
        'HBA1C'                   : sim_hba1c,
        'Fasting_Blood_Sugar'     : float(sim_fbs),
        'BMI'                     : sim_bmi,
        'Postprandial_Blood_Sugar': float(sim_ppbs),
        'Physical_Activity'       : sim_activity,
        'Stress_Level'            : sim_stress,
        'Smoking_Status'          : sim_smoking,
    })
    sim_results  = predict(sim_data, models)
    sim_prob     = sim_results['ensemble']['probability']
    sim_risk     = sim_results['ensemble']['risk_level']
    risk_change  = sim_prob - orig_prob
    change_color = '#2ecc71' if risk_change < 0 else '#e74c3c'
    change_sign  = '▼' if risk_change < 0 else '▲'

    with result_col:
        st.markdown("**Live Risk Comparison:**")

        st.markdown(f"""
        <div class='metric-card' style='border-left-color:#3498db;'>
            <div style='font-size:13px; color:#7f8c8d;'>
                Original Risk</div>
            <div style='font-size:28px; font-weight:700;
                        color:{RISK_COLORS[original["ensemble"]["risk_level"]]};'>
                {RISK_ICONS[original['ensemble']['risk_level']]}
                {original['ensemble']['risk_level']}
                ({orig_prob*100:.1f}%)
            </div>
        </div>
        <div class='metric-card'
             style='border-left-color:{RISK_COLORS[sim_risk]};'>
            <div style='font-size:13px; color:#7f8c8d;'>
                Simulated Risk</div>
            <div style='font-size:28px; font-weight:700;
                        color:{RISK_COLORS[sim_risk]};'>
                {RISK_ICONS[sim_risk]} {sim_risk}
                ({sim_prob*100:.1f}%)
            </div>
        </div>
        <div class='metric-card'
             style='border-left-color:{change_color};'>
            <div style='font-size:13px; color:#7f8c8d;'>
                Risk Change</div>
            <div style='font-size:28px; font-weight:700;
                        color:{change_color};'>
                {change_sign} {abs(risk_change)*100:.1f}%
            </div>
            <div style='font-size:12px; color:#7f8c8d;'>
                {'Risk decreased ✓' if risk_change < 0
                 else 'Risk increased ⚠️' if risk_change > 0
                 else 'No change'}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Probability gauge
        fig_gauge = go.Figure(go.Indicator(
            mode  = "gauge+number+delta",
            value = sim_prob * 100,
            delta = {'reference': orig_prob * 100,
                     'valueformat': '.1f'},
            title = {'text': "Simulated Risk %"},
            gauge = {
                'axis'  : {'range': [0, 100]},
                'bar'   : {'color': RISK_COLORS[sim_risk]},
                'steps' : [
                    {'range': [0, 30],  'color': '#d5f5e3'},
                    {'range': [30, 60], 'color': '#fef9e7'},
                    {'range': [60, 100],'color': '#fdedec'},
                ],
                'threshold': {
                    'line' : {'color': 'black', 'width': 2},
                    'value': orig_prob * 100
                }
            },
            number = {'suffix': '%', 'valueformat': '.1f'}
        ))
        fig_gauge.update_layout(
            height=250,
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=40, b=0)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

# ── TAB 2: Recovery Simulation ────────────────────────────
with tab2:
    st.markdown(
        "<div class='info-box'>"
        "This simulation applies <b>realistic 3-month "
        "lifestyle improvements</b> to your profile and "
        "calculates your projected risk. Changes are based on "
        "clinically achievable targets per ICMR guidelines."
        "</div>",
        unsafe_allow_html=True
    )

    if st.button("▶  Run 90-Day Recovery Simulation",
                 type="primary"):
        with st.spinner("Simulating 90-day recovery..."):
            recovery = simulate_recovery(
                form_data, orig_prob, models
            )

        st.session_state['recovery'] = recovery

    if st.session_state.get('recovery'):
        rec = st.session_state['recovery']

        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.metric(
                "Current Risk",
                f"{rec['current_proba']*100:.1f}%",
                delta=None
            )
        with rc2:
            st.metric(
                "Projected Risk (90 days)",
                f"{rec['simulated_proba']*100:.1f}%",
                delta=f"-{rec['risk_reduction']*100:.1f}%"
            )
        with rc3:
            st.metric(
                "Risk Reduction",
                f"{rec['risk_reduction_pct']:.1f}%",
                delta=f"{RISK_ICONS[rec['projected_risk']]} {rec['projected_risk']}"
            )

        st.markdown("**Changes Applied in Simulation:**")
        if rec['changes_applied']:
            for change in rec['changes_applied']:
                st.markdown(f"  ✅ {change}")
        else:
            st.markdown(
                "*Your current lifestyle profile already "
                "reflects optimal values — focus on clinical "
                "management.*"
            )

        # Before/after bar
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x     = ['Current Risk', 'Projected Risk (90 days)'],
            y     = [rec['current_proba']*100,
                     rec['simulated_proba']*100],
            marker_color = [
                RISK_COLORS[original['ensemble']['risk_level']],
                RISK_COLORS[rec['projected_risk']]
            ],
            text  = [f"{rec['current_proba']*100:.1f}%",
                     f"{rec['simulated_proba']*100:.1f}%"],
            textposition = 'outside',
            width = 0.4
        ))
        fig_bar.update_layout(
            title  = '90-Day Risk Projection',
            yaxis  = dict(range=[0, 100], title='Risk %'),
            height = 320,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_bar, use_container_width=True)