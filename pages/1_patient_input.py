# ============================================================
# pages/1_patient_input.py — Patient Data Input
# ============================================================
# WHAT: Structured input form grouped into Clinical,
#       Lifestyle, and Comorbidity sections
# WHY GROUPED: Shows domain understanding. Clinical features
#   (HbA1c, FBS) are things a doctor measures. Lifestyle
#   features (stress, activity) are things a patient controls.
#   Mixing them in one flat form loses this distinction.
# ============================================================

import streamlit as st
from config import CATEGORICAL_OPTIONS
from config import THEMES
from modules.utils import get_theme_css


st.set_page_config(
    page_title="Patient Input — DiabetesIQ",
    page_icon="📋", layout="wide"
)



# Inherit theme from session state (set in app.py)
theme_name = st.session_state.get('theme_name', 'Dark')
theme      = THEMES[theme_name]
st.markdown(get_theme_css(theme), unsafe_allow_html=True)


st.markdown("## 📋 Patient Data Input")
st.markdown(
    "Enter the patient's clinical and lifestyle data below. "
    "Fields are grouped by domain — **Clinical**, **Lifestyle**, "
    "and **Comorbidities**."
)
st.markdown("<hr>", unsafe_allow_html=True)

# ── SECTION 1: Clinical Features ─────────────────────────
st.markdown(
    "<div class='section-header'>🏥 Section 1 — Clinical Markers</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='info-box'>These values come from blood tests "
    "and physical measurements. They are the strongest "
    "predictors of diabetes risk.</div>",
    unsafe_allow_html=True
)

c1, c2, c3 = st.columns(3)

with c1:
    age = st.number_input(
        "Age (years)", min_value=18, max_value=90,
        value=35, step=1,
        help="Patient's current age in years"
    )
    hba1c = st.number_input(
        "HbA1c (%)", min_value=4.0, max_value=15.0,
        value=5.5, step=0.1,
        help="Glycated haemoglobin. Normal < 5.7%, Pre-diabetic 5.7–6.4%, Diabetic ≥ 6.5%"
    )
    fasting_bs = st.number_input(
        "Fasting Blood Sugar (mg/dL)", min_value=60, max_value=300,
        value=95, step=1,
        help="Normal < 100, Pre-diabetic 100–125, Diabetic ≥ 126 mg/dL"
    )
    postprandial_bs = st.number_input(
        "Postprandial Blood Sugar (mg/dL)", min_value=80, max_value=400,
        value=130, step=1,
        help="2-hour post meal glucose. Diabetic threshold ≥ 200 mg/dL"
    )

with c2:
    bmi = st.number_input(
        "BMI (kg/m²)", min_value=14.0, max_value=50.0,
        value=24.0, step=0.1,
        help="Indian overweight threshold: 23. Indian obese threshold: 27.5"
    )
    waist_hip = st.number_input(
        "Waist-Hip Ratio", min_value=0.60, max_value=1.30,
        value=0.88, step=0.01,
        help="Abdominal obesity indicator. High risk: >0.90 (men), >0.85 (women)"
    )
    cholesterol = st.number_input(
        "Cholesterol Level (mg/dL)", min_value=100, max_value=400,
        value=175, step=1,
        help="Total cholesterol. Desirable < 200 mg/dL"
    )
    heart_rate = st.number_input(
        "Heart Rate (bpm)", min_value=40, max_value=150,
        value=75, step=1,
        help="Resting heart rate in beats per minute"
    )

with c3:
    glucose_tolerance = st.number_input(
        "Glucose Tolerance Test (mg/dL)", min_value=60, max_value=400,
        value=130, step=1,
        help="OGTT result. Diabetic threshold ≥ 200 mg/dL"
    )
    vitamin_d = st.number_input(
        "Vitamin D Level (ng/mL)", min_value=5.0, max_value=80.0,
        value=28.0, step=0.5,
        help="Deficiency (<20) linked to insulin resistance"
    )
    c_protein = st.number_input(
        "C-Reactive Protein (mg/L)", min_value=0.1, max_value=20.0,
        value=3.0, step=0.1,
        help="Inflammation marker. Elevated CRP associated with insulin resistance"
    )
    pregnancies = st.number_input(
        "Number of Pregnancies", min_value=0, max_value=15,
        value=0, step=1,
        help="Total number of pregnancies (enter 0 for male patients)"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── SECTION 2: Lifestyle Features ────────────────────────
st.markdown(
    "<div class='section-header'>🏃 Section 2 — Lifestyle Factors</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='info-box'>These are modifiable risk factors — "
    "the ones a patient can actively change. SHAP will show "
    "which of these is most impacting your risk.</div>",
    unsafe_allow_html=True
)

l1, l2, l3, l4 = st.columns(4)

with l1:
    gender = st.selectbox(
        "Gender", CATEGORICAL_OPTIONS['Gender'],
        help="Biological sex"
    )
    physical_activity = st.selectbox(
        "Physical Activity Level",
        CATEGORICAL_OPTIONS['Physical_Activity'],
        help="Low = sedentary, Medium = moderate exercise, High = regular vigorous exercise"
    )

with l2:
    diet_type = st.selectbox(
        "Diet Type", CATEGORICAL_OPTIONS['Diet_Type'],
        help="Primary dietary pattern"
    )
    stress_level = st.selectbox(
        "Stress Level", CATEGORICAL_OPTIONS['Stress_Level'],
        help="Perceived daily stress level"
    )

with l3:
    smoking_status = st.selectbox(
        "Smoking Status", CATEGORICAL_OPTIONS['Smoking_Status'],
        help="Current smoking behaviour"
    )
    alcohol_intake = st.selectbox(
        "Alcohol Intake", CATEGORICAL_OPTIONS['Alcohol_Intake'],
        help="Frequency/amount of alcohol consumption"
    )

with l4:
    urban_rural = st.selectbox(
        "Urban / Rural", CATEGORICAL_OPTIONS['Urban_Rural'],
        help="Living environment — urban populations have higher processed food access"
    )
    health_insurance = st.selectbox(
        "Health Insurance", CATEGORICAL_OPTIONS['Health_Insurance'],
        help="Access to healthcare"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── SECTION 3: Comorbidities ──────────────────────────────
st.markdown(
    "<div class='section-header'>🫀 Section 3 — Comorbidities & History</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='info-box'>Pre-existing conditions and family "
    "history. These compound diabetes risk significantly.</div>",
    unsafe_allow_html=True
)

m1, m2, m3 = st.columns(3)

with m1:
    hypertension = st.selectbox(
        "Hypertension", CATEGORICAL_OPTIONS['Hypertension'],
        help="Diagnosed high blood pressure"
    )
    family_history = st.selectbox(
        "Family History of Diabetes",
        CATEGORICAL_OPTIONS['Family_History'],
        help="First-degree relative with diabetes"
    )

with m2:
    thyroid = st.selectbox(
        "Thyroid Condition", CATEGORICAL_OPTIONS['Thyroid_Condition'],
        help="Diagnosed thyroid disorder"
    )
    pcos = st.selectbox(
        "Polycystic Ovary Syndrome (PCOS)",
        CATEGORICAL_OPTIONS['Polycystic_Ovary_Syndrome'],
        help="Relevant for female patients — PCOS increases diabetes risk 4x"
    )

with m3:
    medication = st.selectbox(
        "Medication for Chronic Conditions",
        CATEGORICAL_OPTIONS['Medication_For_Chronic_Conditions'],
        help="Currently taking medication for any chronic condition"
    )
    regular_checkups = st.selectbox(
        "Regular Health Checkups",
        CATEGORICAL_OPTIONS['Regular_Checkups'],
        help="Has regular preventive health screenings"
    )

st.markdown("<br><hr>", unsafe_allow_html=True)

# ── SUBMIT BUTTON ─────────────────────────────────────────
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    submit = st.button(
        "🔍  Analyse Risk Profile",
        use_container_width=True,
        type="primary"
    )

if submit:
    # Build form data dictionary
    form_data = {
        'Age'                              : age,
        'Gender'                           : gender,
        'BMI'                              : bmi,
        'Family_History'                   : family_history,
        'Physical_Activity'                : physical_activity,
        'Diet_Type'                        : diet_type,
        'Smoking_Status'                   : smoking_status,
        'Alcohol_Intake'                   : alcohol_intake,
        'Stress_Level'                     : stress_level,
        'Hypertension'                     : hypertension,
        'Cholesterol_Level'                : float(cholesterol),
        'Fasting_Blood_Sugar'              : float(fasting_bs),
        'Postprandial_Blood_Sugar'         : float(postprandial_bs),
        'HBA1C'                            : hba1c,
        'Heart_Rate'                       : heart_rate,
        'Waist_Hip_Ratio'                  : waist_hip,
        'Urban_Rural'                      : urban_rural,
        'Health_Insurance'                 : health_insurance,
        'Regular_Checkups'                 : regular_checkups,
        'Medication_For_Chronic_Conditions': medication,
        'Pregnancies'                      : pregnancies,
        'Polycystic_Ovary_Syndrome'        : pcos,
        'Glucose_Tolerance_Test_Result'    : float(glucose_tolerance),
        'Vitamin_D_Level'                  : vitamin_d,
        'C_Protein_Level'                  : c_protein,
        'Thyroid_Condition'                : thyroid,
    }

    # Store in session state — shared across all pages
    st.session_state['form_data'] = form_data
    st.session_state['data_submitted'] = True

    st.success(
        "✅ Data saved successfully. "
        "Navigate to **Page 2: Risk Dashboard** in the sidebar."
    )
    st.balloons()
else:
    if not st.session_state.get('data_submitted'):
        st.markdown(
            "<div class='warning-box'>⚠️ Fill in all sections above "
            "and click <b>Analyse Risk Profile</b> to proceed.</div>",
            unsafe_allow_html=True
        )