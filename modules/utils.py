# ============================================================
# modules/utils.py — Input Preprocessing Utilities
# ============================================================
# WHAT: Functions that convert raw user input from the UI
#       into the exact format the trained models expect
# WHY:  The model was trained on encoded + scaled data.
#       Raw input ("Male", 28.5, "High") must go through
#       the same transformations before prediction.
#       Keeping this separate means UI code stays clean.
# ============================================================

import pandas as pd
#import numpy as np
#from config import CATEGORICAL_OPTIONS


def build_raw_input(form_data: dict) -> pd.DataFrame:
    """
    Convert UI form dictionary into a single-row DataFrame
    matching the original dataset's column structure.

    Args:
        form_data: dict of {feature_name: value} from UI

    Returns:
        pd.DataFrame with one row, all original columns present
    """
    return pd.DataFrame([form_data])


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the same feature engineering from Step 4 of the notebook.
    Must mirror EXACTLY what was done during training.

    WHY: If training used BMI_Category but prediction doesn't
         compute it → model receives wrong feature set → crash.
    """
    df = df.copy()

    # --- BMI Category (Indian thresholds — ICMR 2023) ---
    def bmi_category(bmi):
        if bmi < 18.5:
            return 'Underweight'
        elif bmi < 23:
            return 'Normal'
        elif bmi < 27.5:
            return 'Overweight'
        else:
            return 'Obese'

    df['BMI_Category'] = df['BMI'].apply(bmi_category)

    # --- Age Group ---
    def age_group(age):
        if age < 30:
            return 'Young'
        elif age < 45:
            return 'Middle'
        else:
            return 'Senior'

    df['Age_Group'] = df['Age'].apply(age_group)

    # --- HbA1c Category (WHO diagnostic bands) ---
    def hba1c_category(val):
        if val < 5.7:
            return 'Normal'
        elif val < 6.5:
            return 'Pre_Diabetic'
        else:
            return 'Diabetic_Range'

    df['HbA1c_Category'] = df['HBA1C'].apply(hba1c_category)

    # --- Fasting Blood Sugar Category ---
    def fbs_category(val):
        if val < 100:
            return 'Normal'
        elif val < 126:
            return 'Pre_Diabetic'
        else:
            return 'Diabetic_Range'

    df['FBS_Category'] = df['Fasting_Blood_Sugar'].apply(fbs_category)

    # --- Lifestyle Risk Score ---
    def lifestyle_risk(row):
        score = 0
        if row['Smoking_Status'] in ['Current', 'Former']:
            score += 1
        if row['Alcohol_Intake'] in ['Heavy', 'Moderate']:
            score += 1
        if row['Physical_Activity'] == 'Low':
            score += 1
        if row['Stress_Level'] == 'High':
            score += 1
        return score

    df['Lifestyle_Risk_Score'] = df.apply(lifestyle_risk, axis=1)

    # --- Comorbidity Score ---
    def comorbidity(row):
        score = 0
        if row['Hypertension'] == 'Yes':
            score += 1
        if row['Thyroid_Condition'] == 'Yes':
            score += 1
        if str(row['Polycystic_Ovary_Syndrome']) == 'Yes':
            score += 1
        if row['Medication_For_Chronic_Conditions'] == 'Yes':
            score += 1
        return score

    df['Comorbidity_Score'] = df.apply(comorbidity, axis=1)

    # --- BMI × Activity Interaction ---
    activity_map = {'Low': 1, 'Medium': 2, 'High': 3}
    df['BMI_Activity_Index'] = (
        df['BMI'] * df['Physical_Activity'].map(activity_map)
    )

    # --- Clinical Risk Index ---
    df['Clinical_Risk_Index'] = (
        (df['HBA1C'] / 12.0) * 0.5 +
        (df['Fasting_Blood_Sugar'] / 180.0) * 0.3 +
        (df['Postprandial_Blood_Sugar'] / 300.0) * 0.2
    )

    return df


def encode_and_scale(df: pd.DataFrame,
                     label_encoders: dict,
                     scaler,
                     feature_names: list) -> pd.DataFrame:
    """
    Apply label encoding and standard scaling — same as training.

    Args:
        df            : DataFrame after feature engineering
        label_encoders: dict of fitted LabelEncoders from training
        scaler        : fitted StandardScaler from training
        feature_names : exact list of features model expects

    Returns:
        Processed DataFrame ready for model prediction
    """
    df = df.copy()

    # --- Label encode categorical columns ---
    cat_cols = df.select_dtypes(include='object').columns.tolist()
    for col in cat_cols:
        if col in label_encoders:
            le = label_encoders[col]
            # Handle unseen categories gracefully
            df[col] = df[col].apply(
                lambda x: x if x in le.classes_ else le.classes_[0]
            )
            df[col] = le.transform(df[col])

    # --- Scale numerical columns ---
    num_cols = df.select_dtypes(
        include=['int64', 'float64']
    ).columns.tolist()
    df[num_cols] = scaler.transform(df[num_cols])

    # --- Ensure exact feature order model expects ---
    df = df[feature_names]

    return df


def get_risk_level(probability: float) -> str:
    """Convert raw probability to Low / Medium / High."""
    if probability < 0.30:
        return 'Low'
    elif probability < 0.60:
        return 'Medium'
    else:
        return 'High'


def compute_radar_scores(form_data: dict) -> dict:
    """
    Compute 0–100 scores for each Risk DNA radar axis.
    Used for the radar chart on the dashboard page.

    Each axis score = weighted average of its component features,
    normalised to 0–100 range.
    """
    scores = {}

    # Clinical axis — HbA1c + FBS dominate
    hba1c_score = min((form_data.get('HBA1C', 5.0) / 12.0) * 100, 100)
    fbs_score   = min((form_data.get('Fasting_Blood_Sugar', 90) / 180.0) * 100, 100)
    ppbs_score  = min((form_data.get('Postprandial_Blood_Sugar', 120) / 300.0) * 100, 100)
    scores['Clinical'] = round((hba1c_score * 0.5 + fbs_score * 0.3 + ppbs_score * 0.2), 1)

    # Metabolic axis — BMI + Waist-Hip Ratio
    bmi_score = min((form_data.get('BMI', 22) / 40.0) * 100, 100)
    whr_score = min((form_data.get('Waist_Hip_Ratio', 0.8) / 1.2) * 100, 100)
    chol_score = min((form_data.get('Cholesterol_Level', 150) / 300.0) * 100, 100)
    scores['Metabolic'] = round((bmi_score * 0.4 + whr_score * 0.35 + chol_score * 0.25), 1)

    # Lifestyle axis — activity, stress, smoking, alcohol
    activity_risk  = {'Low': 80, 'Medium': 40, 'High': 10}
    stress_risk    = {'High': 80, 'Medium': 40, 'Low': 10}
    smoking_risk   = {'Current': 80, 'Former': 50, 'Never': 5}
    alcohol_risk   = {'Heavy': 80, 'Moderate': 45,
                      'None': 5, 'Not_Reported': 20}

    scores['Lifestyle'] = round((
        activity_risk.get(form_data.get('Physical_Activity', 'Medium'), 40) * 0.3 +
        stress_risk.get(form_data.get('Stress_Level', 'Medium'), 40) * 0.3 +
        smoking_risk.get(form_data.get('Smoking_Status', 'Never'), 5) * 0.2 +
        alcohol_risk.get(form_data.get('Alcohol_Intake', 'None'), 20) * 0.2
    ), 1)

    # Comorbidity axis
    comorbidity_count = sum([
        form_data.get('Hypertension', 'No') == 'Yes',
        form_data.get('Thyroid_Condition', 'No') == 'Yes',
        form_data.get('Polycystic_Ovary_Syndrome', 'No') == 'Yes',
        form_data.get('Medication_For_Chronic_Conditions', 'No') == 'Yes',
    ])
    scores['Comorbidity'] = round(min(comorbidity_count / 4 * 100, 100), 1)

    # Demographic axis — age + family history
    age = form_data.get('Age', 30)
    age_score    = min(max((age - 20) / 60 * 100, 0), 100)
    family_score = 80 if form_data.get('Family_History', 'No') == 'Yes' else 10
    scores['Demographic'] = round((age_score * 0.6 + family_score * 0.4), 1)

    return scores



#Theme related code for Block/White Light Theme.
def get_theme_css(theme: dict) -> str:

    if theme is None:
        return ""

    """
    Generate complete CSS for the selected theme.
    Called once per page load and injected via st.markdown().

    WHY single function: All theme-dependent CSS lives here.
    Pages just call get_theme_css(theme) — no CSS scattered
    across multiple files.
    """
    return f"""
    <style>
        /* ── Base & Background ── */
        .stApp {{
            background-color: {theme.get('bg_primary', '#FFFFFF')} !important;
        }}
        section[data-testid="stSidebar"] {{
            background-color: {theme.get('sidebar_bg', '#F7F9FC')} !important;
        }}
        section[data-testid="stSidebar"] * {{
            color: {theme.get('sidebar_text', '#000000')} !important;
        }}
        .main .block-container {{
            background-color: {theme.get('bg_primary', '#FFFFFF')};
            padding-top: 2rem;
        }}

        /* ── Typography ── */
        .stApp, .stApp p, .stApp li, .stApp label {{
            color: {theme.get('text_primary', '#000000')} !important;
        }}
        h1, h2, h3 {{
            color: {theme.get('section_header', '#000000')} !important;
        }}

        /* ── Input Widgets ── */
        .stTextInput input, .stNumberInput input,
        .stSelectbox select, div[data-baseweb="select"] {{
            background-color: {theme.get('bg_secondary', '#F5F5F5')} !important;
            color: {theme.get('text_primary', '#000000')} !important;
            border-color: {theme.get('border', '#000000')} !important;
        }}
        div[data-baseweb="select"] > div {{
            background-color: {theme.get('bg_secondary', '#F5F5F5')} !important;
            color: {theme.get('text_primary', '#000000')} !important;
        }}
        .stSlider > div {{
            color: {theme.get('text_primary', '#000000')} !important;
        }}

        /* ── Metric Cards ── */
        .metric-card {{
            background: {theme.get('bg_card', '#FFFFFF')};
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px {theme.get('shadow', '#000000')};
            border-left: 4px solid {theme.get('metric_border', '#000000')};
            margin-bottom: 16px;
            color: {theme.get('text_primary', '#000000')};
        }}

        /* ── Section Header ── */
        .section-header {{
            font-size: 18px;
            font-weight: 600;
            color: {theme.get('section_header', '#000000')};
            border-bottom: 2px solid {theme.get('accent', '#000000')};
            padding-bottom: 6px;
            margin-bottom: 16px;
        }}

        /* ── Info / Warning / Insight Boxes ── */
        .info-box {{
            background: {theme.get('info_bg', '#FFFFFF')};
            border-left: 4px solid {theme.get('info_border', '#000000')};
            border-radius: 6px;
            padding: 12px 16px;
            margin: 8px 0;
            font-size: 14px;
            color: {theme.get('text_primary', '#000000')};
        }}
        .warning-box {{
            background: {theme.get('warning_bg', '#FFFFFF')};
            border-left: 4px solid {theme.get('warning_border', '#000000')};
            border-radius: 6px;
            padding: 12px 16px;
            margin: 8px 0;
            font-size: 14px;
            color: {theme.get('text_primary', '#000000')};
        }}
        .insight-box {{
            background: {theme.get('insight_bg', '#FFFFFF')};
            border-left: 4px solid {theme.get('insight_border', '#000000')};
            border-radius: 6px;
            padding: 12px 16px;
            margin: 8px 0;
            font-size: 14px;
            color: {theme.get('text_primary', '#000000')};
        }}

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: {theme.get('bg_secondary', '#F5F5F5')};
            border-radius: 8px;
        }}
        .stTabs [data-baseweb="tab"] {{
            color: {theme.get('text_secondary', '#000000')} !important;
        }}
        .stTabs [aria-selected="true"] {{
            color: {theme.get('accent', '#000000')} !important;
        }}

        /* ── Dataframes & Tables ── */
        .stDataFrame {{
            background-color: {theme.get('bg_card', '#FFFFFF')} !important;
        }}

        /* ── Plotly chart backgrounds ── */
        .js-plotly-plot .plotly {{
            background: transparent !important;
        }}

        /* ── Code blocks ── */
        code, pre {{
            background-color: {theme.get('code_bg', '#FFFFFF')} !important;
            color: {theme.get('text_primary', '#000000')} !important;
            border-radius: 6px;
        }}

        /* ── Buttons ── */
        .stButton > button {{
            background-color: {theme.get('accent', '#000000')};
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            font-weight: 600;
        }}
        .stButton > button:hover {{
            background-color: {theme.get('accent', '#000000')};
            opacity: 0.85;
            border: none;
        }}

        /* ── Metrics ── */
        [data-testid="metric-container"] {{
            background-color: {theme.get('bg_card', '#FFFFFF')};
            border: 1px solid {theme.get('border', '#000000')};
            border-radius: 10px;
            padding: 12px;
        }}

        /* ── Hide default elements ── */
        #MainMenu {{ visibility: hidden; }}
        footer    {{ visibility: hidden; }}
    </style>
    """
    # /* Navigation Bar Text */
    #     .stSidebar .block-container .element-container:first-child * {
    #         color: {theme.get('sidebar_text', '#000000')} !important;
    #     }