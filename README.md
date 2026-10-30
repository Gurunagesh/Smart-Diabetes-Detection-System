# 🩺 DiabetesIQ — Smart Diabetes Detection System

> Explainable diabetes risk screening for the Indian population, built with Streamlit, scikit-learn, XGBoost, SHAP and PyTorch.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![XGBoost](https://img.shields.io/badge/XGBoost-Model-green)
![SHAP](https://img.shields.io/badge/Explainability-SHAP-orange)
![License](https://img.shields.io/badge/License-Apache%202.0-lightgrey)

> ⚠️ **Disclaimer:** This is an academic screening tool, **not** a medical device. It does not diagnose diabetes. Always consult a qualified healthcare professional.

---

## 📌 Overview

India has an estimated **101M+ adults living with diabetes** and **136M with pre-diabetes** (ICMR 2023), and a large share of cases go undiagnosed. Many existing prediction tools are trained on Western data (e.g. the PIMA dataset), return an unexplained yes/no, ignore lifestyle factors, and do not use Indian BMI thresholds.

**DiabetesIQ** addresses these gaps. It estimates diabetes risk from clinical, lifestyle and comorbidity inputs, explains *why* with SHAP, benchmarks the user against Indian population averages, and simulates how risk could change after 90 days of realistic lifestyle improvements.

## ✨ Key Features

| Feature | Description |
|---|---|
| 🧬 **Risk DNA** | 5-axis radar profile (Clinical, Metabolic, Lifestyle, Comorbidity, Demographic) |
| 🤖 **Dual-model prediction** | Logistic Regression + XGBoost, averaged into an ensemble probability |
| 🤝 **Model agreement score** | Flags borderline cases where the two models disagree |
| 🔍 **SHAP explainability** | Per-patient feature contributions and a Clinical vs Lifestyle vs Comorbidity split |
| 🔮 **What-if simulator** | Adjust any input manually, or run an automatic 90-day recovery projection |
| 💡 **Personalised insights** | Recommendations driven by the factors that actually push *this* patient's risk |
| 🇮🇳 **Indian context** | Indian BMI cut-offs and comparison with ICMR population averages |
| 🌗 **Light / Dark theme** | Persistent theme toggle across all pages |

## 🖥️ App Pages

1. **Patient Input**: form grouped into Clinical, Lifestyle and Comorbidity sections.
2. **Risk Dashboard**: ensemble score, Low/Medium/High band, dual-model comparison, Risk DNA radar, SHAP chart.
3. **What-if Simulator**: manual explorer with a live risk gauge, plus the 90-day recovery simulation.
4. **Insights**: personalised explanations, ranked recommendations and Indian population benchmarking.

## 🧠 How It Works

```
Patient input → Feature engineering (+8) → Encode & scale → LR + XGBoost → Ensemble risk
                                                                │
                                                                └→ SHAP (TreeExplainer on XGBoost)
                                                                       → Insights · Risk DNA · Simulator
```

### Engineered features (27 → 34 columns)

| Feature | Definition |
|---|---|
| `Clinical_Risk_Index` | `HbA1c/12 × 0.5 + FBS/180 × 0.3 + PPBS/300 × 0.2` |
| `BMI_Category` | Underweight < 18.5 · Normal < 23 · Overweight < 27.5 · Obese ≥ 27.5 (Indian thresholds) |
| `HbA1c_Category` | Normal < 5.7 · Pre-diabetic 5.7–6.4 · Diabetic range ≥ 6.5 (WHO bands) |
| `FBS_Category` | Normal < 100 · Pre-diabetic 100–125 · Diabetic range ≥ 126 mg/dL |
| `Age_Group` | Young < 30 · Middle < 45 · Senior |
| `Lifestyle_Risk_Score` | Smoking + alcohol + low activity + high stress (0–4) |
| `Comorbidity_Score` | Hypertension + thyroid + PCOS + chronic medication (0–4) |
| `BMI_Activity_Index` | BMI × activity level (Low = 1, Medium = 2, High = 3) |

### Risk bands and decision threshold

| Level | Ensemble probability |
|---|---|
| 🟢 Low | 0.00 – 0.30 |
| 🟡 Medium | 0.30 – 0.60 |
| 🔴 High | 0.60 – 1.00 |

A **0.10 decision threshold** is used for both models. Lowering it from the default 0.50 prioritises **recall**, because in screening a missed case is costlier than a false alarm. The trade-off is lower precision (see results).

### Model agreement

`agreement = max(0, 1 − |p_LR − p_XGB| / 0.5)`: above 0.85 is *High confidence*, above 0.60 is *Moderate*, otherwise *Borderline, seek clinical evaluation*.

## 📊 Dataset

- **Source:** Kaggle.com
- **Size:** 5,292 patient records, 26 input features + target (`Diabetes_Status`)
- **Feature groups:** Clinical (HbA1c, fasting & postprandial glucose, BMI, waist-hip ratio, glucose tolerance, cholesterol, heart rate, vitamin D, C-protein, age, pregnancies), Lifestyle (activity, diet, smoking, alcohol, stress, urban/rural, insurance, check-ups), Comorbidity (hypertension, thyroid, PCOS, chronic medication, family history, gender)
- **Cleaning:** PCOS column had mixed types (`0`/`No`/`Yes`) and was normalised; 1,780 missing alcohol values were handled without dropping rows.

### ⚠️ Important note on labels

During EDA the original Kaggle labels showed essentially **no correlation** with clinical markers (HbA1c: −0.019, fasting blood sugar: −0.002), and about 1,920 patients with diabetic-range HbA1c were labelled non-diabetic. The notebook therefore **reconstructs the labels** using a weighted clinical risk score based on ICMR/WHO criteria (HbA1c, fasting, postprandial and OGTT glucose, plus BMI, hypertension, family history and inactivity), thresholded at the 45th percentile (→ ~55% / 45% class split). HbA1c's correlation with the target rises to about +0.70.

**What this means for the results:** because the labels are computed from the same inputs the models see, the near-perfect metrics below show how well the models recover that scoring rule. They are **not** evidence of real-world diagnostic accuracy. Validation on real, clinician-labelled data is the most important next step.

> `models/diabetes.csv` in this repo is the original Kaggle file with its original labels; the reconstruction happens inside the notebook.

## 🏋️ Training & Results

Full pipeline in [`Diabetes_project.ipynb`](Diabetes_project.ipynb): preprocessing → EDA → feature engineering → model comparison → threshold optimisation → tuning → deep-learning experiment → SHAP.

- **Split:** stratified 80/20 (4,233 train / 1,059 test)
- **Validation:** 5-fold stratified cross-validation on the training set
- **Tuning:** `RandomizedSearchCV` for LR and XGBoost
- **Models compared:** Logistic Regression, Decision Tree, Random Forest, XGBoost, plus a PyTorch MLP (128→64→32, BatchNorm, Dropout, Adam, early stopping)

### 5-fold cross-validation (before tuning)

| Model | CV Accuracy | CV F1 | CV ROC-AUC | CV Recall | Overfit gap |
|---|---|---|---|---|---|
| **Logistic Regression** | 0.9913 | 0.9920 | 0.9998 | 0.9897 | 0.0031 |
| XGBoost | 0.9802 | 0.9820 | 0.9987 | 0.9824 | 0.0198 |
| Random Forest | 0.9445 | 0.9493 | 0.9915 | 0.9450 | 0.0215 |
| Decision Tree | 0.9504 | 0.9547 | 0.9870 | 0.9497 | 0.0145 |

### Tuned models on the held-out test set (threshold = 0.10)

| Model | Accuracy | F1 | ROC-AUC | Precision | Recall |
|---|---|---|---|---|---|
| **Logistic Regression (tuned)** | 0.99 | 0.99 | 1.00 | 0.98 | 1.00 |
| XGBoost (tuned) | 0.97 | 0.97 | 1.00 | 0.94 | 1.00 |
| Deep Learning (MLP) | 0.96 | 0.97 | 1.00 | 0.94 | 1.00 |

Tuning cut XGBoost's train–test overfit gap from 0.040 to 0.014. Logistic Regression outperformed the MLP, in line with research suggesting simpler models are competitive on small tabular datasets (Grinsztajn et al., NeurIPS 2022).

### SHAP findings (tuned XGBoost, test set)

Top features by mean |SHAP|: `Clinical_Risk_Index` (7.25, far ahead of the rest), `Glucose_Tolerance_Test_Result` (1.85), `Family_History` (1.66), `Hypertension` (1.62), `BMI` (1.44), `Fasting_Blood_Sugar` (0.84), `BMI_Activity_Index` (0.60). Since `Clinical_Risk_Index` is built from the same markers used to construct the labels, its dominance is expected (see the note on labels above).

## 📁 Project Structure

```
Smart-Diabetes-Detection-System/
├── app.py                          # Entry point: landing page, theme toggle, sidebar
├── config.py                       # Paths, thresholds, risk bands, ICMR averages, themes
├── requirements.txt
├── Diabetes_project.ipynb          # Full training notebook (EDA → models → SHAP)
├── DiabetesIQ_Presentation_guru_PPT4.pptx   # Project presentation
├── pages/
│   ├── 1_patient_input.py
│   ├── 2_risk_dashboard.py
│   ├── 3_simulator.py
│   └── 4_insights.py
├── modules/
│   ├── predictor.py                # Model loading and prediction pipeline
│   ├── explainer.py                # SHAP computation and plots
│   ├── recommender.py              # Insights and 90-day recovery simulation
│   └── utils.py                    # Feature engineering, encoding, radar scores, CSS
├── models/
│   ├── lr_final_model.pkl
│   ├── xgb_final_model.pkl
│   ├── scaler.pkl
│   ├── label_encoders.pkl
│   ├── model_config.json           # 34 feature names + thresholds
│   └── diabetes.csv                # Original Kaggle dataset
└── .devcontainer/                  # GitHub Codespaces / VS Code dev container
```

## 🚀 Getting Started

**Prerequisites:** Python 3.11 (recommended) and pip.

```bash
# 1. Clone (code lives on the master branch)
git clone -b master https://github.com/Gurunagesh/Smart-Diabetes-Detection-System.git
cd Smart-Diabetes-Detection-System

# 2. (Optional) virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
streamlit run app.py
```

Open **http://localhost:8501**. The repo also ships a dev container, so it runs automatically in GitHub Codespaces.

To retrain the models, open `Diabetes_project.ipynb` in Google Colab, upload `diabetes.csv`, and run the cells in order.

## 🛠️ Tech Stack

Streamlit · scikit-learn · XGBoost · SHAP · PyTorch (experiment) · pandas · NumPy · Plotly · Matplotlib · joblib

## ⚠️ Limitations

- **Labels are rule-derived** from clinical markers (see above), so reported metrics do not reflect real-world diagnostic performance.
- The **0.10 threshold** gives recall ≈ 1.00 at the cost of more false positives (LR precision ≈ 0.93 before tuning).
- The recovery simulation applies fixed, illustrative improvements, not clinically validated projections.
- Lab values (HbA1c, glucose) should come from real tests, not estimates.
- Not a substitute for professional medical advice.

## 🔭 Future Scope

Validation on real clinician-labelled data · federated learning · IoT / wearable integration · multilingual UI · EHR / HIS integration

## 🎓 Academic Context

Developed at **Aditya College of Engineering & Technology (A)**, Department of Computer Science & Engineering. Guide: **Mr. M. Kiran Bhagavan**. Academic year 2025–2026.

## 📄 License

Licensed under the **Apache License 2.0**. See [`LICENSE`](LICENSE).

## 👤 Author

**Gurunagesh**: [GitHub](https://github.com/Gurunagesh)
