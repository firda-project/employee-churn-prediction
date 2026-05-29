<!-- Project Title & Catchy Description
Key Features
Tech Stack / Prerequisites
Installation & Setup Instructions
Usage Example
Contributing Guidelines (Optional but recommended)
License -->

# TalentPulse: Employee Turnover & Retention Risk Analytics

**TalentPulse** is a data-driven workforce analytics platform built with Streamlit and powered by Machine Learning (Logistic Regression $t = 0.40$). It enables HR team, team leads, and board of directors to monitor employee demographics, identify systemic churn drivers, and proactively predict the resignation probability of single or multiple employees simultaneously.

---
## Preview
![Preview](https://res.cloudinary.com/dtwqkecvp/image/upload/v1780049783/new_dashboard_fz3lie.png)


---
> 🚀 Try it live: [TalentPulse Dashboard](https://talentpulse-blackbox.streamlit.app/)
---

## Key Modules

The application is split into three main actionable dashboards:

### 1. Employee Turnover Dashboard
* **Workforce Demographics:** Interactive visualizations mapping churn trends across gender, education level, work location, and marital status using `Plotly`.
* **Workload & Operational Catalysts:** Tracks correlation metrics between sales/performance target deficits, excessive overtime ratios, commuting distances, and overall churn.
* **Dynamic Filtering:** Refine data via custom sidebar widgets exploring Job Satisfaction Level and Manager Support Scores ($1$ to $4$).

### 2. Single Employee Prediction
* **Real-time Risk Assessment:** Evaluate an individual employee's retention status using a Logistic Regression model ($t = 0.40$ tuned classification threshold).
* **Prescriptive Recommendations:** Generates contextual HR strategies directly tailored to the individual's specific stress points (e.g., severe overtime or weak manager backing).

### 3. Batch/Bulk Prediction
* **Enterprise Scaling:** Upload large-scale `.csv` or `.xlsx` sheets to batch-predict churn across entire departments in seconds.
* **Data Quality Validation:** Integrated automated preprocessing engine that catches formatting errors, corrupted strings, or out-of-bounds metrics before pushing data to the model pipeline.
* **Automated Action Plan Generation:** Exports prediction tables directly back into custom-styled Excel sheets formatted with embedded risk-mitigation strategies.

---
## Model Performance

TalentPulse uses a **Logistic Regression** model with a custom classification threshold of **t = 0.40**, selected from 29 model variants across 8 algorithms based on maximizing Recall while minimizing the train-test recall gap.

### Why Logistic Regression?
- Achieves the same Recall as more complex models (Stacking, MLP) with simpler architecture
- More interpretable and deployable for HR use cases
- Models with perfect Recall (XGBoost, SVM) were flagged as **overfit** and excluded

### Final Model Metrics

| Metric | Score |
|--------|-------|
| Recall | **0.944** |
| Precision | 0.672 |
| F1-Score | 0.785 |
| ROC-AUC | 0.712 |
| Recall Gap (Train vs Test) | 0.006 |

> **Why Recall as primary metric?** Missing an at-risk employee (false negative) costs 0.5–2× their annual salary in replacement. A false positive only costs a minor HR intervention.

### Top Predictive Features
Selected via `SelectKBest` with `f_classif` scoring:
1. `target_achievement` — employee's monthly target completion rate
2. `overall_satisfaction` — engineered feature: job satisfaction × manager support score
3. `unachieved_target` — engineered feature: (1 - target_achievement) × monthly target
4. `distance_to_office_km` — commute distance from home to office
5. `distance_group_Far` — binary flag: employee lives >25 km from office
---
## Tech Stack & Architecture

* **Frontend UI:** Streamlit
* **Data Analysis & Processing:** Pandas, NumPy, OpenPyXL
* **Data Visualization:** Plotly Express & Plotly Graph Objects
* **Machine Learning Backend:** Scikit-Learn (Logistic Regression Pipeline packaged via Joblib)

---
## Installation Setup

### Prerequisites
- Python 3.9+
- pip

### Steps

1. **Clone the repository**
```bash
   git clone https://github.com/firda-project/employee-churn-prediction.git
   cd employee-churn-prediction
```

2. **Create and activate virtual environment** *(recommended)*
```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Mac/Linux
   python -m venv venv
   source venv/bin/activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Run the application**
```bash
   streamlit run app.py
```

5. **Open in browser**
```
   http://localhost:8501
```
---
## Contributors/Team

| Name | Role | GitHub |
|------|------|--------|
| Josephine Bianca Rucita | Project Manager & Data Scientist | [@biancarucita16](https://github.com/biancarucita16) |
| Yehezkiel Marbun Lumbanbatu | Data/Business Analyst | [@xeyzel](https://github.com/xeyzel) |
| Firda Angzalna Putri | Data Engineer | [@firda-project](https://github.com/firda-project) |

---
## Acknowledgements

- **Rakamin Academy** — for providing the learning framework and project simulation environment
- **Muhammad Hanif Fajari** — project mentor, for guidance throughout the development process

---

### Project Directory Structure
```text
talentpulse/

    data/
       employee_churn_prediction_updated.csv

    models/
       model_lr.pkl       # Logistic Regression pipeline & custom threshold

    utils.py               # Feature extraction & strategy generator algorithms
    style.css              # Custom dashboard presentation markup/style
    app.py                 # Multi-page main application runner (individual app sheets: dashboard, single prediction, batch prediction)
    requirements.txt       # Software dependencies manifest
    README.md              # Project Documentation