# ============================================================
# modules/predictor.py — Model Loading & Prediction
# ============================================================
# WHAT: Loads trained models once, runs predictions,
#       returns structured results for both LR and XGBoost
# WHY:  Centralising model logic means pages never touch
#       .pkl files directly — clean separation of concerns
# ============================================================

import joblib
import json
#import numpy as np
import streamlit as st
from config import MODEL_PATHS, THRESHOLDS
from modules.utils import (build_raw_input, engineer_features,
                            encode_and_scale, get_risk_level)


@st.cache_resource
def load_models():
    """
    Load all model artifacts once and cache them.

    WHY @st.cache_resource:
        Streamlit reruns the entire script on every interaction.
        Without caching, models reload on every button click.
        cache_resource keeps them in memory — fast and efficient.
    """
    lr      = joblib.load(MODEL_PATHS['lr'])
    xgb     = joblib.load(MODEL_PATHS['xgb'])
    scaler  = joblib.load(MODEL_PATHS['scaler'])
    encoders = joblib.load(MODEL_PATHS['encoders'])

    with open(MODEL_PATHS['config'], 'r') as f:
        config = json.load(f)

    return {
        'lr'      : lr,
        'xgb'     : xgb,
        'scaler'  : scaler,
        'encoders': encoders,
        'features': config['feature_names'],
    }


def predict(form_data: dict, models: dict) -> dict:
    """
    Full prediction pipeline for one patient.

    Args:
        form_data: raw dict of user inputs from the UI
        models   : loaded model artifacts from load_models()

    Returns:
        dict with lr and xgb results, risk levels, agreement
    """
    # Step 1: Build raw DataFrame
    raw_df = build_raw_input(form_data)

    # Step 2: Engineer features (same as training Step 4)
    engineered_df = engineer_features(raw_df)

    # Step 3: Encode + scale (same as training Step 2)
    processed_df = encode_and_scale(
        engineered_df,
        models['encoders'],
        models['scaler'],
        models['features']
    )

    # Step 4: Predict with both models
    lr_proba  = models['lr'].predict_proba(processed_df)[0][1]
    xgb_proba = models['xgb'].predict_proba(processed_df)[0][1]

    lr_pred  = int(lr_proba  >= THRESHOLDS['lr'])
    xgb_pred = int(xgb_proba >= THRESHOLDS['xgb'])

    # Step 5: Risk levels
    lr_risk  = get_risk_level(lr_proba)
    xgb_risk = get_risk_level(xgb_proba)

    # Step 6: Model agreement score
    # WHY: If both models agree → high confidence
    #      If they disagree → borderline, flag for clinical review
    prob_diff   = abs(lr_proba - xgb_proba)
    agreement   = max(0, 1 - (prob_diff / 0.5))  # 0–1 scale
    agree_label = (
        'High Confidence'    if agreement > 0.85 else
        'Moderate Confidence' if agreement > 0.60 else
        'Borderline — seek clinical evaluation'
    )

    # Step 7: Ensemble probability (average of both)
    ensemble_proba = (lr_proba + xgb_proba) / 2
    ensemble_risk  = get_risk_level(ensemble_proba)

    return {
        'lr': {
            'probability': round(float(lr_proba), 4),
            'prediction' : lr_pred,
            'risk_level' : lr_risk,
        },
        'xgb': {
            'probability': round(float(xgb_proba), 4),
            'prediction' : xgb_pred,
            'risk_level' : xgb_risk,
        },
        'ensemble': {
            'probability': round(float(ensemble_proba), 4),
            'risk_level' : ensemble_risk,
        },
        'agreement': {
            'score': round(float(agreement), 4),
            'label': agree_label,
        },
        'processed_input': processed_df,
    }