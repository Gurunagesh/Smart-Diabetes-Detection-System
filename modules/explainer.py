# ============================================================
# modules/explainer.py — SHAP Explainability
# ============================================================
# WHAT: Compute SHAP values for a single patient prediction
#       and format them for display in the UI
# WHY:  SHAP computation is slow — isolating it here means
#       we can cache the explainer object separately and
#       only recompute values when input actually changes
# ============================================================

import shap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from config import MODEL_PATHS
import joblib


@st.cache_resource
def load_explainer(_xgb_model):
    """
    Create and cache the SHAP TreeExplainer.
    WHY prefix _: Streamlit can't hash model objects —
    underscore prefix tells it to skip hashing this arg.
    """
    return shap.TreeExplainer(_xgb_model)


def get_shap_values(processed_input, explainer, feature_names: list) -> dict:
    """
    Compute SHAP values for a single patient input.

    Returns dict with:
        values      : raw SHAP values array
        df          : sorted DataFrame for display
        top_positive: top features increasing risk
        top_negative: top features decreasing risk
        base_value  : model's baseline (expected) output
    """
    input_array = processed_input.values

    # Compute SHAP values
    shap_vals = explainer.shap_values(input_array)[0]

    # Build display DataFrame
    shap_df = pd.DataFrame({
        'Feature'    : feature_names,
        'SHAP_Value' : shap_vals,
        'Direction'  : ['↑ Risk' if v > 0 else '↓ Risk' for v in shap_vals],
        'Impact'     : np.abs(shap_vals),
    }).sort_values('Impact', ascending=False).reset_index(drop=True)

    # Percentage contribution
    total_impact = shap_df['Impact'].sum()
    shap_df['Contribution_%'] = (
        (shap_df['Impact'] / total_impact * 100).round(1)
    )

    return {
        'values'      : shap_vals,
        'df'          : shap_df,
        'top_positive': shap_df[shap_df['SHAP_Value'] > 0].head(5),
        'top_negative': shap_df[shap_df['SHAP_Value'] < 0].head(5),
        'base_value'  : explainer.expected_value,
        'total_impact': total_impact,
    }


def plot_shap_bar(shap_dict: dict, top_n: int = 12) -> plt.Figure:
    """
    Horizontal bar chart of top SHAP contributors.
    Red = increases risk, Green = decreases risk.
    """
    df = shap_dict['df'].head(top_n).sort_values('SHAP_Value')

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#e74c3c' if v > 0 else '#2ecc71' for v in df['SHAP_Value']]

    bars = ax.barh(df['Feature'], df['SHAP_Value'],
                   color=colors, edgecolor='white', linewidth=1)

    # Value labels
    for bar, val, pct in zip(bars, df['SHAP_Value'],
                              df['Contribution_%']):
        x_pos = val + (0.02 if val >= 0 else -0.02)
        ha    = 'left' if val >= 0 else 'right'
        ax.text(x_pos, bar.get_y() + bar.get_height()/2,
                f'{val:+.3f} ({pct:.1f}%)',
                va='center', ha=ha, fontsize=8, fontweight='bold')

    ax.axvline(x=0, color='black', linewidth=1)
    ax.set_xlabel('SHAP Value (impact on diabetes risk prediction)')
    ax.set_title('Feature Contribution to Your Risk Prediction\n'
                 'Red = increases risk  |  Green = decreases risk',
                 fontweight='bold', pad=12)
    ax.grid(True, alpha=0.3, axis='x')
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    plt.tight_layout()
    return fig


def compute_domain_shap(shap_dict: dict) -> dict:
    """
    Aggregate SHAP values by clinical domain for the
    Clinical vs Lifestyle risk split panel.

    Groups features into Clinical, Lifestyle, Comorbidity
    and returns total positive SHAP contribution per group.
    """
    from config import CLINICAL_FEATURES, LIFESTYLE_FEATURES, COMORBIDITY_FEATURES

    df = shap_dict['df']

    domain_scores = {}
    for domain, features in [
        ('Clinical',    CLINICAL_FEATURES),
        ('Lifestyle',   LIFESTYLE_FEATURES),
        ('Comorbidity', COMORBIDITY_FEATURES),
    ]:
        domain_df = df[df['Feature'].isin(features)]
        # Sum only positive SHAP (risk-increasing contributions)
        pos_shap  = domain_df[domain_df['SHAP_Value'] > 0]['SHAP_Value'].sum()
        domain_scores[domain] = round(float(pos_shap), 4)

    return domain_scores