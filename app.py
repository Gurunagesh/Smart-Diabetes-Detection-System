# ============================================================
# app.py — Entry Point
# ============================================================
# WHAT: Main entry point for the Streamlit app.
#       Handles page configuration, styling, and navigation.
# WHY:  Kept minimal — only routing and global config here.
#       All logic lives in pages/ and modules/.
# ============================================================

import streamlit as st
from config import APP_TITLE, APP_SUBTITLE, APP_VERSION

# --- Page configuration — must be first Streamlit call ---
st.set_page_config(
    page_title     = "DiabetesIQ",
    page_icon      = "🩺",
    layout         = "wide",
    initial_sidebar_state = "expanded"
)

# --- Global CSS styling ---
st.markdown("""
<style>
    /* Main background */
    .main { background-color: #f8f9fa; }

    /* Sidebar */
    .css-1d391kg { background-color: #1a1a2e; }

    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #3498db;
        margin-bottom: 16px;
    }

    /* Risk badge */
    .risk-high   { color: #e74c3c; font-size: 28px; font-weight: 700; }
    .risk-medium { color: #f39c12; font-size: 28px; font-weight: 700; }
    .risk-low    { color: #2ecc71; font-size: 28px; font-weight: 700; }

    /* Section headers */
    .section-header {
        font-size: 18px;
        font-weight: 600;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 6px;
        margin-bottom: 16px;
    }

    /* Info box */
    .info-box {
        background: #eaf4fb;
        border-left: 4px solid #3498db;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 14px;
    }

    /* Warning box */
    .warning-box {
        background: #fef9e7;
        border-left: 4px solid #f39c12;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 14px;
    }

    /* Insight box */
    .insight-box {
        background: #f0fff4;
        border-left: 4px solid #2ecc71;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 14px;
    }

    /* Hide default streamlit menu */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar navigation header ---
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding: 20px 0 10px;'>
        <div style='font-size:42px;'>🩺</div>
        <div style='font-size:20px; font-weight:700;
                    color:#2c3e50;'>{APP_TITLE}</div>
        <div style='font-size:12px; color:#7f8c8d;
                    margin-top:4px;'>{APP_SUBTITLE}</div>
        <div style='font-size:11px; color:#bdc3c7;
                    margin-top:8px;'>v{APP_VERSION}</div>
    </div>
    <hr style='margin: 10px 0; border-color: #ecf0f1;'>
    """, unsafe_allow_html=True)

    st.markdown("### 📋 Navigation")
    st.markdown("""
    1. **Patient Input** — Enter clinical & lifestyle data
    2. **Risk Dashboard** — View risk DNA and model results
    3. **What-if Simulator** — Explore risk changes live
    4. **Insights** — Personalised recommendations
    """)

    st.markdown("<hr style='border-color:#ecf0f1;'>", unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:11px; color:#95a5a6; padding: 10px 0;'>
        <b>Models:</b> Logistic Regression (primary)<br>
        + XGBoost (secondary)<br><br>
        <b>Explainability:</b> SHAP TreeExplainer<br><br>
        <b>Population:</b> Indian clinical norms<br>
        (ICMR 2023 guidelines)<br><br>
        ⚠️ For academic and screening purposes only.
        Not a substitute for clinical diagnosis.
    </div>
    """, unsafe_allow_html=True)

# --- Landing page content ---
st.markdown(f"""
<div style='text-align:center; padding: 40px 0 20px;'>
    <div style='font-size:56px;'>🩺</div>
    <h1 style='font-size:36px; color:#2c3e50;
               font-weight:700;'>{APP_TITLE}</h1>
    <p style='font-size:16px; color:#7f8c8d;
              max-width:600px; margin:0 auto;'>
        {APP_SUBTITLE}
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class='metric-card'>
        <div style='font-size:28px;'>🧬</div>
        <div style='font-weight:600; margin-top:8px;'>
            Risk DNA Analysis</div>
        <div style='font-size:13px; color:#7f8c8d; margin-top:4px;'>
            5-axis radar profile unique to each patient</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='metric-card'>
        <div style='font-size:28px;'>🔍</div>
        <div style='font-weight:600; margin-top:8px;'>
            SHAP Explainability</div>
        <div style='font-size:13px; color:#7f8c8d; margin-top:4px;'>
            Understand exactly why your risk is high or low</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='metric-card'>
        <div style='font-size:28px;'>🔮</div>
        <div style='font-weight:600; margin-top:8px;'>
            Recovery Simulation</div>
        <div style='font-size:13px; color:#7f8c8d; margin-top:4px;'>
            Project your risk after 90-day lifestyle changes</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class='metric-card'>
        <div style='font-size:28px;'>🇮🇳</div>
        <div style='font-weight:600; margin-top:8px;'>
            Indian Population Context</div>
        <div style='font-size:13px; color:#7f8c8d; margin-top:4px;'>
            Benchmarked against ICMR national averages</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.info("👈 Use the sidebar to navigate. Start with **Page 1: Patient Input** to enter your data.")