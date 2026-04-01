# ============================================================
# app.py — Entry Point with Theme Toggle
# ============================================================

import streamlit as st
from config import APP_TITLE, APP_SUBTITLE, APP_VERSION, THEMES
from modules.utils import get_theme_css

st.set_page_config(
    page_title     = "DiabetesIQ",
    page_icon      = "🩺",
    layout         = "wide",
    initial_sidebar_state = "expanded"
)

# ── Theme initialisation ──────────────────────────────────
# WHY session_state: persists the theme choice as user
# navigates between all 4 pages
if 'theme_name' not in st.session_state:
    st.session_state['theme_name'] = 'Dark'  # default matches current look

theme_name = st.session_state['theme_name']
theme      = THEMES[theme_name]

# Inject theme CSS globally
st.markdown(get_theme_css(theme), unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    # Theme toggle — at the very top of sidebar
    st.markdown("### ⚙️ Appearance")

    col_light, col_dark = st.columns(2)
    with col_light:
        if st.button(
            "☀️ Light",
            use_container_width=True,
            type="primary" if theme_name == 'Light' else "secondary"
        ):
            st.session_state['theme_name'] = 'Light'
            st.rerun()
    with col_dark:
        if st.button(
            "🌙 Dark",
            use_container_width=True,
            type="primary" if theme_name == 'Dark' else "secondary"
        ):
            st.session_state['theme_name'] = 'Dark'
            st.rerun()

    st.markdown(
        f"<hr style='border-color:{theme['border']};margin:12px 0;'>",
        unsafe_allow_html=True
    )

    # App branding
    st.markdown(f"""
    <div style='text-align:center; padding: 10px 0;'>
        <div style='font-size:38px;'>🩺</div>
        <div style='font-size:17px; font-weight:700;
                    color:{theme["sidebar_text"]};'>
            {APP_TITLE}
        </div>
        <div style='font-size:11px; color:{theme["text_muted"]};
                    margin-top:4px;'>{APP_SUBTITLE}</div>
        <div style='font-size:10px; color:{theme["text_muted"]};
                    margin-top:6px;'>v{APP_VERSION}</div>
    </div>
    <hr style='border-color:{theme["border"]}; margin:10px 0;'>
    """, unsafe_allow_html=True)

    st.markdown(
        f"<div style='color:{theme['sidebar_text']};'>### 📋 Navigation</div>",
        unsafe_allow_html=True
    )
    st.markdown(f"""
    <div style='font-size:13px; color:{theme["sidebar_text"]}; line-height:2;'>
        1. <b>Patient Input</b> — Clinical &amp; lifestyle data<br>
        2. <b>Risk Dashboard</b> — Risk DNA &amp; model results<br>
        3. <b>What-if Simulator</b> — Explore risk changes live<br>
        4. <b>Insights</b> — Personalised recommendations
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"<hr style='border-color:{theme['border']};'>",
        unsafe_allow_html=True
    )
    st.markdown(f"""
    <div style='font-size:11px; color:{theme["text_muted"]}; padding:8px 0;'>
        <b>Models:</b> Logistic Regression + XGBoost<br>
        <b>Explainability:</b> SHAP TreeExplainer<br>
        <b>Population:</b> ICMR 2023 Indian norms<br><br>
        ⚠️ Academic screening tool only.
    </div>
    """, unsafe_allow_html=True)

# ── Landing page ──────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center; padding:40px 0 24px;'>
    <div style='font-size:52px;'>🩺</div>
    <h1 style='font-size:34px; color:{theme["text_primary"]};
               font-weight:700; margin:12px 0 8px;'>
        {APP_TITLE}
    </h1>
    <p style='font-size:15px; color:{theme["text_secondary"]};
              max-width:560px; margin:0 auto;'>
        {APP_SUBTITLE}
    </p>
</div>
""", unsafe_allow_html=True)

# Feature cards
c1, c2, c3, c4 = st.columns(4)
cards = [
    ("🧬", "Risk DNA Analysis",
     "5-axis radar profile unique to each patient"),
    ("🔍", "SHAP Explainability",
     "Understand exactly why your risk is high or low"),
    ("🔮", "Recovery Simulation",
     "Project your risk after 90-day lifestyle changes"),
    ("🇮🇳", "Indian Population Context",
     "Benchmarked against ICMR national averages"),
]
for col, (icon, title, desc) in zip([c1, c2, c3, c4], cards):
    with col:
        st.markdown(f"""
        <div class='metric-card'>
            <div style='font-size:26px;'>{icon}</div>
            <div style='font-weight:600; margin-top:8px;
                        color:{theme["text_primary"]};
                        font-size:14px;'>{title}</div>
            <div style='font-size:12px;
                        color:{theme["text_secondary"]};
                        margin-top:4px;'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.info(
    "👈 Use the sidebar to navigate. "
    "Start with **Page 1: Patient Input** to enter your data."
)