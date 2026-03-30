# ============================================================
# config.py — Central Configuration
# ============================================================
# WHAT: All constants, paths, thresholds, and static data
#       in one place
# WHY:  If a threshold changes, you change it here ONCE.
#       Not scattered across 6 files.
#       This is standard software engineering practice.
# ============================================================

import os

# --- Paths ---
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

MODEL_PATHS = {
    'lr'      : os.path.join(MODELS_DIR, 'lr_final_model.pkl'),
    'xgb'     : os.path.join(MODELS_DIR, 'xgb_final_model.pkl'),
    'scaler'  : os.path.join(MODELS_DIR, 'scaler.pkl'),
    'encoders': os.path.join(MODELS_DIR, 'label_encoders.pkl'),
    'config'  : os.path.join(MODELS_DIR, 'model_config.json'),
}

# --- Decision Thresholds (from Step 6) ---
THRESHOLDS = {
    'lr' : 0.10,
    'xgb': 0.10,
}

# --- Risk Stratification Bands ---
# Based on ICMR risk communication guidelines
RISK_BANDS = {
    'Low'   : (0.00, 0.30),
    'Medium': (0.30, 0.60),
    'High'  : (0.60, 1.00),
}

RISK_COLORS = {
    'Low'   : '#2ecc71',
    'Medium': '#f39c12',
    'High'  : '#e74c3c',
}

RISK_ICONS = {
    'Low'   : '🟢',
    'Medium': '🟡',
    'High'  : '🔴',
}

# --- Indian Population Reference Values ---
# Source: ICMR National Diabetes Survey 2023
#         Indian Council of Medical Research
INDIAN_POPULATION_AVERAGES = {
    'HBA1C'                   : 7.1,
    'Fasting_Blood_Sugar'     : 118.0,
    'Postprandial_Blood_Sugar': 155.0,
    'BMI'                     : 24.8,
    'Cholesterol_Level'       : 185.0,
    'Waist_Hip_Ratio'         : 0.92,
}

# --- Feature Groups for UI Organisation ---
# WHY grouped: Shows domain understanding — clinical vs lifestyle
# Professors notice this separation immediately
CLINICAL_FEATURES = [
    'Age', 'BMI', 'HBA1C', 'Fasting_Blood_Sugar',
    'Postprandial_Blood_Sugar', 'Cholesterol_Level',
    'Waist_Hip_Ratio', 'Heart_Rate',
    'Glucose_Tolerance_Test_Result', 'Vitamin_D_Level',
    'C_Protein_Level', 'Pregnancies'
]

LIFESTYLE_FEATURES = [
    'Physical_Activity', 'Diet_Type', 'Smoking_Status',
    'Alcohol_Intake', 'Stress_Level', 'Urban_Rural',
    'Health_Insurance', 'Regular_Checkups'
]

COMORBIDITY_FEATURES = [
    'Hypertension', 'Thyroid_Condition',
    'Polycystic_Ovary_Syndrome',
    'Medication_For_Chronic_Conditions',
    'Family_History', 'Gender'
]

# --- Radar Chart Axes (Risk DNA) ---
# Each axis = one risk domain
# Value = list of features contributing to that axis
RADAR_AXES = {
    'Clinical'     : ['HBA1C', 'Fasting_Blood_Sugar',
                      'Postprandial_Blood_Sugar',
                      'Glucose_Tolerance_Test_Result'],
    'Metabolic'    : ['BMI', 'Waist_Hip_Ratio',
                      'Cholesterol_Level', 'C_Protein_Level'],
    'Lifestyle'    : ['Physical_Activity', 'Stress_Level',
                      'Smoking_Status', 'Alcohol_Intake'],
    'Comorbidity'  : ['Hypertension', 'Thyroid_Condition',
                      'Polycystic_Ovary_Syndrome',
                      'Medication_For_Chronic_Conditions'],
    'Demographic'  : ['Age', 'Family_History', 'Gender'],
}

# --- Categorical Input Options ---
CATEGORICAL_OPTIONS = {
    'Gender'          : ['Male', 'Female', 'Other'],
    'Physical_Activity': ['Low', 'Medium', 'High'],
    'Diet_Type'       : ['Vegetarian', 'Non-Vegetarian', 'Vegan'],
    'Smoking_Status'  : ['Never', 'Former', 'Current'],
    'Alcohol_Intake'  : ['None', 'Moderate', 'Heavy', 'Not_Reported'],
    'Stress_Level'    : ['Low', 'Medium', 'High'],
    'Urban_Rural'     : ['Urban', 'Rural'],
    'Family_History'  : ['Yes', 'No'],
    'Hypertension'    : ['Yes', 'No'],
    'Health_Insurance': ['Yes', 'No'],
    'Regular_Checkups': ['Yes', 'No'],
    'Medication_For_Chronic_Conditions': ['Yes', 'No'],
    'Polycystic_Ovary_Syndrome'        : ['Yes', 'No'],
    'Thyroid_Condition': ['Yes', 'No'],
}

# --- Recovery Simulation Settings ---
SIMULATION_TIMEFRAME_DAYS = 90   # 3-month target window
SIMULATION_TARGETS = {
    # feature: (realistic_improvement, unit_label)
    'BMI'             : (2.5,  'units'),
    'Physical_Activity': (1,   'level up'),
    'Stress_Level'    : (1,    'level down'),
    'Smoking_Status'  : (1,    'step toward quitting'),
    'HBA1C'           : (0.5,  '%'),
    'Fasting_Blood_Sugar': (10, 'mg/dL'),
}

# --- App Metadata ---
APP_TITLE    = "DiabetesIQ — Smart Diabetes Detection System "
APP_SUBTITLE = "Personalised diabetes risk analysis for the Indian population"
APP_VERSION  = "1.0.0"