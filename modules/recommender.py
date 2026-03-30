# ============================================================
# modules/recommender.py — Personalised Insight Engine
# ============================================================
# WHAT: Generate personalised, SHAP-driven text insights
#       and actionable recommendations per patient
# WHY:  Generic advice ("exercise more") is useless.
#       SHAP tells us WHICH specific factors are driving
#       THIS patient's risk → we generate advice targeting
#       exactly those factors.
# ============================================================

from config import INDIAN_POPULATION_AVERAGES, SIMULATION_TARGETS


def generate_insights(form_data: dict,
                      shap_dict: dict,
                      risk_level: str) -> dict:
    """
    Generate personalised insights based on SHAP values
    and patient input data.

    Returns:
        dict with primary_driver, insights list,
        recommendations list, indian_context list
    """
    top_features = shap_dict['df'].head(5)['Feature'].tolist()
    shap_df      = shap_dict['df']

    insights        = []
    recommendations = []
    indian_context  = []

    # --- Primary Risk Driver ---
    top_feature = shap_df.iloc[0]['Feature']
    top_shap    = shap_df.iloc[0]['SHAP_Value']
    top_pct     = shap_df.iloc[0]['Contribution_%']

    primary_driver = (
        f"Your risk is primarily driven by **{top_feature.replace('_', ' ')}**, "
        f"contributing {top_pct:.1f}% of your total risk score."
    )

    # --- HbA1c Insight ---
    hba1c = form_data.get('HBA1C', 5.0)
    if hba1c >= 6.5:
        insights.append(
            f"Your HbA1c of {hba1c}% is in the **diabetic range** (≥6.5%). "
            f"This is the strongest clinical marker for diabetes diagnosis per WHO criteria."
        )
        recommendations.append(
            "Consult an endocrinologist for HbA1c management. "
            "Target HbA1c below 7.0% with medication and dietary changes."
        )
    elif hba1c >= 5.7:
        insights.append(
            f"Your HbA1c of {hba1c}% indicates **pre-diabetes** (5.7–6.4%). "
            f"Early intervention now can prevent progression."
        )
        recommendations.append(
            "Reduce refined carbohydrates and increase whole grains. "
            "A 5–7% weight reduction can bring HbA1c to normal range."
        )

    # --- BMI Insight (Indian thresholds) ---
    bmi = form_data.get('BMI', 22)
    if bmi >= 27.5:
        insights.append(
            f"Your BMI of {bmi:.1f} exceeds the Indian obesity threshold of 27.5. "
            f"Asian populations develop insulin resistance at lower BMI than Western norms."
        )
        recommendations.append(
            f"Target a BMI reduction of 2–3 units over 3 months through "
            f"caloric deficit of 300–500 kcal/day combined with 150 min/week exercise."
        )
    elif bmi >= 23:
        insights.append(
            f"Your BMI of {bmi:.1f} is in the Indian overweight range (23–27.5). "
            f"Even modest weight loss reduces diabetes risk significantly."
        )

    # --- Fasting Blood Sugar Insight ---
    fbs = form_data.get('Fasting_Blood_Sugar', 90)
    if fbs >= 126:
        insights.append(
            f"Your fasting blood sugar of {fbs:.0f} mg/dL meets the clinical "
            f"diabetes threshold (≥126 mg/dL). Clinical evaluation is recommended."
        )
        recommendations.append(
            "Avoid refined sugars and processed foods. "
            "Follow the Indian Diabetes Diet guidelines — 50% complex carbs, "
            "25% protein, 25% healthy fats."
        )
    elif fbs >= 100:
        insights.append(
            f"Your fasting blood sugar of {fbs:.0f} mg/dL is in the pre-diabetic "
            f"range (100–125 mg/dL). Dietary management can normalise this."
        )

    # --- Lifestyle Insights ---
    if form_data.get('Physical_Activity') == 'Low':
        insights.append(
            "Low physical activity is a significant modifiable risk factor. "
            "Indians with sedentary lifestyles have 2.5x higher diabetes risk."
        )
        recommendations.append(
            "Begin with 30 minutes of brisk walking 5 days/week. "
            "Even 10-minute post-meal walks reduce postprandial glucose by 15–20%."
        )

    if form_data.get('Stress_Level') == 'High':
        insights.append(
            "Chronic high stress elevates cortisol, which directly raises "
            "blood glucose and promotes abdominal fat storage."
        )
        recommendations.append(
            "Incorporate 10–15 minutes of pranayama or meditation daily. "
            "Clinical studies show stress reduction lowers HbA1c by 0.3–0.5%."
        )

    if form_data.get('Smoking_Status') == 'Current':
        insights.append(
            "Active smoking increases diabetes risk by 30–40% through "
            "nicotine-induced insulin resistance."
        )
        recommendations.append(
            "Smoking cessation is the single highest-impact lifestyle change. "
            "Consult a cessation programme — risk reduces significantly within 5 years."
        )

    # --- Comorbidity Insights ---
    if form_data.get('Hypertension') == 'Yes':
        insights.append(
            "Hypertension and diabetes frequently co-occur — 70% of Indian "
            "diabetics also have hypertension. Managing BP reduces diabetes risk."
        )

    if form_data.get('Family_History') == 'Yes':
        insights.append(
            "Family history indicates genetic predisposition. "
            "While unmodifiable, it makes lifestyle factors MORE critical to manage."
        )

    # --- Indian Population Context ---
    for feature, avg in INDIAN_POPULATION_AVERAGES.items():
        user_val = form_data.get(feature)
        if user_val is not None:
            diff = user_val - avg
            direction = "above" if diff > 0 else "below"
            pct_diff  = abs(diff / avg * 100)
            if pct_diff > 10:
                indian_context.append(
                    f"**{feature.replace('_', ' ')}**: Your value of "
                    f"{user_val:.1f} is {pct_diff:.0f}% {direction} the "
                    f"Indian population average of {avg}."
                )

    # Limit to top 5 most relevant
    insights        = insights[:6]
    recommendations = recommendations[:5]
    indian_context  = indian_context[:4]

    return {
        'primary_driver'  : primary_driver,
        'insights'        : insights,
        'recommendations' : recommendations,
        'indian_context'  : indian_context,
        'risk_level'      : risk_level,
    }


def simulate_recovery(form_data: dict,
                      current_proba: float,
                      models: dict) -> dict:
    """
    Compute projected risk after applying realistic
    3-month lifestyle improvements.

    WHY this matters:
        Shows patients a concrete achievable target,
        not an abstract risk score.
    """
    from modules.utils import (build_raw_input, engineer_features,
                                encode_and_scale, get_risk_level)

    simulated = form_data.copy()
    changes_made = []

    # Apply realistic 3-month improvements where applicable
    if simulated.get('Physical_Activity') == 'Low':
        simulated['Physical_Activity'] = 'Medium'
        changes_made.append("Physical activity: Low → Medium")

    if simulated.get('Stress_Level') == 'High':
        simulated['Stress_Level'] = 'Medium'
        changes_made.append("Stress level: High → Medium")

    if simulated.get('Smoking_Status') == 'Current':
        simulated['Smoking_Status'] = 'Former'
        changes_made.append("Smoking: Current → Former")

    # Realistic BMI reduction: 2 units in 3 months
    if simulated.get('BMI', 22) > 25:
        simulated['BMI'] = max(simulated['BMI'] - 2.0, 22)
        changes_made.append(f"BMI: {form_data['BMI']:.1f} → {simulated['BMI']:.1f}")

    # Realistic FBS improvement
    if simulated.get('Fasting_Blood_Sugar', 90) > 110:
        simulated['Fasting_Blood_Sugar'] = max(
            simulated['Fasting_Blood_Sugar'] - 10, 90
        )
        changes_made.append(
            f"Fasting Blood Sugar: {form_data['Fasting_Blood_Sugar']:.0f}"
            f" → {simulated['Fasting_Blood_Sugar']:.0f} mg/dL"
        )

    # Run prediction on simulated inputs
    raw_df        = build_raw_input(simulated)
    engineered_df = engineer_features(raw_df)
    processed_df  = encode_and_scale(
        engineered_df,
        models['encoders'],
        models['scaler'],
        models['features']
    )

    sim_lr_proba  = models['lr'].predict_proba(processed_df)[0][1]
    sim_xgb_proba = models['xgb'].predict_proba(processed_df)[0][1]
    sim_proba     = (sim_lr_proba + sim_xgb_proba) / 2

    risk_reduction = current_proba - sim_proba

    return {
        'current_proba'   : round(current_proba, 4),
        'simulated_proba' : round(float(sim_proba), 4),
        'risk_reduction'  : round(float(risk_reduction), 4),
        'risk_reduction_pct': round(float(risk_reduction / current_proba * 100), 1),
        'projected_risk'  : get_risk_level(sim_proba),
        'changes_applied' : changes_made,
        'simulated_inputs': simulated,
    }