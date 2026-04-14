# ============================================================
# pages/4_insights.py — Personalised Insights
# ============================================================
# WHAT: SHAP-driven personalised text insights, actionable
#       recommendations, and Indian population benchmarking
# WHY:  The final output a patient or doctor actually reads.
#       Every insight is specific to THIS patient's SHAP
#       values — not generic diabetes advice.
# ============================================================

import streamlit as st
from modules.predictor   import load_models, predict
from modules.explainer   import load_explainer, get_shap_values
from modules.recommender import generate_insights
from config              import RISK_COLORS, RISK_ICONS, INDIAN_POPULATION_AVERAGES


# Move imports to the top
from config import THEMES
from modules.utils import get_theme_css

# Ensure imports are at the top
st.set_page_config(
    page_title="Insights — DiabetesIQ",
    page_icon="💡", layout="wide"
)

# Inherit theme from session state (set in app.py)
theme_name = st.session_state.get('theme_name', 'Dark')
theme      = THEMES[theme_name]
st.markdown(get_theme_css(theme), unsafe_allow_html=True)

if not st.session_state.get('data_submitted'):
    st.warning("⚠️ No patient data found. Please complete Page 1 first.")
    st.stop()

form_data = st.session_state['form_data']
models    = load_models()

# Load or recompute results
if 'results' not in st.session_state:
    results = predict(form_data, models)
    st.session_state['results'] = results
else:
    results = st.session_state['results']

if 'shap_dict' not in st.session_state:
    explainer = load_explainer(models['xgb'])
    shap_dict = get_shap_values(
        results['processed_input'], explainer, models['features']
    )
    st.session_state['shap_dict'] = shap_dict
else:
    shap_dict = st.session_state['shap_dict']

# Generate insights
insights_data = generate_insights(
    form_data, shap_dict,
    results['ensemble']['risk_level']
)

# ── HEADER ────────────────────────────────────────────────
st.markdown("## 💡 Personalised Insights & Recommendations")
st.markdown(
    "Every insight below is generated specifically for your "
    "risk profile using SHAP values. These are not generic "
    "diabetes tips — they reflect your actual risk drivers."
)
st.markdown("<hr>", unsafe_allow_html=True)

risk_level = results['ensemble']['risk_level']
risk_color = RISK_COLORS[risk_level]

# ── SECTION 1: Primary Driver ─────────────────────────────
st.markdown(
    "<div class='section-header'>🎯 Primary Risk Driver</div>",
    unsafe_allow_html=True
)
st.markdown(f"""
<div class='metric-card' style='border-left-color:{risk_color};
     font-size:16px; line-height:1.6;'>
    {RISK_ICONS[risk_level]} {insights_data['primary_driver']}
</div>
""", unsafe_allow_html=True)

# ── SECTION 2: Clinical Insights ──────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-header'>🔬 Clinical Insights</div>",
    unsafe_allow_html=True
)

if insights_data['insights']:
    for i, insight in enumerate(insights_data['insights'], 1):
        st.markdown(f"""
        <div class='info-box'>
            <b>{i}.</b> {insight}
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown(
        "<div class='insight-box'>✅ No critical clinical "
        "risk factors identified at current values.</div>",
        unsafe_allow_html=True
    )

# ── SECTION 3: Recommendations ────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-header'>"
    "✅ Personalised Action Plan</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='info-box'>"
    "These recommendations are ranked by their potential "
    "impact on your specific risk drivers.</div>",
    unsafe_allow_html=True
)

if insights_data['recommendations']:
    for i, rec in enumerate(insights_data['recommendations'], 1):
        st.markdown(f"""
        <div class='insight-box'>
            <b>Action {i}:</b> {rec}
        </div>
        """, unsafe_allow_html=True)

# ── SECTION 4: Indian Population Benchmarking ─────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-header'>"
    "🇮🇳 Indian Population Benchmarking</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='info-box'>"
    "How your values compare to the Indian population average "
    "(ICMR National Diabetes Survey 2023). "
    "Values more than 10% above average are highlighted."
    "</div>",
    unsafe_allow_html=True
)

bench_cols = st.columns(3)
for i, (feature, avg) in enumerate(
        INDIAN_POPULATION_AVERAGES.items()):
    user_val = form_data.get(feature)
    if user_val is None:
        continue

    diff     = user_val - avg
    pct_diff = diff / avg * 100
    status   = ('⬆️ Above average' if pct_diff > 10
                else '⬇️ Below average' if pct_diff < -10
                else '✅ Near average')
    color    = ('#e74c3c' if pct_diff > 10
                else '#2ecc71' if pct_diff < -10
                else '#3498db')

    with bench_cols[i % 3]:
        st.markdown(f"""
        <div class='metric-card' style='border-left-color:{color};'>
            <div style='font-size:12px; color:{theme.get('text_muted', '#718096')}'>
                {feature.replace('_',' ')}</div>
            <div style='font-size:20px; font-weight:700;
                        color:{theme['text_primary']}'>
                {user_val:.1f}</div>
            <div style='font-size:12px; color:{theme.get('text_muted', '#718096')}'>
                Indian avg: {avg}</div>
            <div style='font-size:12px; color:{color};
                        font-weight:600;'>
                {status} ({pct_diff:+.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)

if insights_data['indian_context']:
    st.markdown("<br>**Context notes:**")
    for note in insights_data['indian_context']:
        st.markdown(f"- {note}")

# ── SECTION 5: Disclaimer ─────────────────────────────────
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("""
<div style='background:#fdfefe; border:1px solid #ecf0f1;
     border-radius:8px; padding:16px; font-size:12px;
     color:#7f8c8d;'>
    ⚠️ <b>Disclaimer:</b> DiabetesIQ is an academic decision
    support tool developed for educational purposes.
    It is not a substitute for professional medical advice,
    diagnosis, or treatment. All outputs should be reviewed
    by a qualified healthcare professional.
    Model trained on Indian population data using ICMR
    clinical guidelines (2023).
</div>
""", unsafe_allow_html=True)