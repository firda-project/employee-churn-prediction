# import library
import pandas as pd
import numpy as np

import joblib
import streamlit as st

from utils import extract_features, get_recommendations



# load model
@st.cache_resource
def load_model():
    return joblib.load('models/model_lr.pkl')

model_data = load_model()
model = model_data['model_pipeline']
threshold = model_data['threshold']

# title
st.title('Single Employee Churn Prediction')
st.markdown('Enter the employee information in the form below to assess the probability of resignation.')
st.divider()

# user inputs
def user_inputs_features():
    st.subheader('Input Employee Data')

    monthly_target = st.number_input(
        '**Monthly Target**',
        min_value=0,
        value=None,
        placeholder='e.g. 100'
    )
    target_achievement = st.number_input(
        '**Target Achievement**',
        value=None,
        placeholder='e.g. 0,85'
    )
    working_hours_per_week = st.number_input(
        '**Working Hours per Week**',
        min_value=0,
        value=None,
        placeholder='e.g. 55'
    )
    overtime_hours_per_week = st.number_input(
        '**Overtime Hours per Week**',
        min_value=0,
        value=None,
        placeholder='e.g. 10'
    )
    job_satisfaction = st.selectbox(
        '**Job Satisfaction**',
        options=[None, 1, 2, 3, 4], 
        index=0,
        format_func=lambda x: "Select Score" if x is None else x
    )
    manager_support_score = st.selectbox(
        '**Manager Support Score**',
        options=[None, 1, 2, 3, 4], 
        index=0,
        format_func=lambda x: "Select Score" if x is None else x
    )
    distance_to_office_km = st.number_input(
        '**Distance to Office (km)**',
        min_value=0,
        value=None,
        placeholder='e.g. 15'
    )

    inputs = {
        'monthly_target': monthly_target,
        'target_achievement': target_achievement,
        'working_hours_per_week': working_hours_per_week,
        'overtime_hours_per_week': overtime_hours_per_week,
        'job_satisfaction': job_satisfaction,
        'manager_support_score': manager_support_score,
        'distance_to_office_km': distance_to_office_km
    }

    return inputs
    

# data input
inputs = user_inputs_features()    

data = {
    'age': np.nan,
    'gender': np.nan,
    'education': np.nan,
    'experience_years': np.nan,
    'monthly_target': inputs['monthly_target'],
    'target_achievement': inputs['target_achievement'],
    'working_hours_per_week': inputs['working_hours_per_week'],
    'overtime_hours_per_week': inputs['overtime_hours_per_week'],
    'salary': np.nan,
    'commission_rate': np.nan,
    'job_satisfaction': inputs['job_satisfaction'],
    'work_location': np.nan,
    'manager_support_score': inputs['manager_support_score'],
    'company_tenure_years': np.nan,
    'marital_status': np.nan,
    'distance_to_office_km': inputs['distance_to_office_km']
}

input_df = pd.DataFrame([data])


# Check empty fields
missing_fields = [k.replace('_', ' ').title() for k, v in inputs.items() if v is None]

if missing_fields:
    # Show the user the unfilled columns
    st.info(f"💡 **Information:** To enable prediction, please fill in: {', '.join(missing_fields)}")
    button_disabled = True
else:
    st.success("✅ All forms are filled. Click **'Predict'** to view the results.")
    button_disabled = False


# Recommendation display
def strategy_recs(pred_label, churn_prob, inputs):
    churn_prob = float(churn_prob)

    inputs['churn_probability'] = churn_prob
    results = get_recommendations(inputs)
    
    if pred_label == 1:
        st.subheader('📋 Strategic Recommendations')
        st.markdown(results['recommendations'])
    else:
        st.subheader("🚀 Engagement Strategy")
        st.markdown(results['recommendations'])


# predict button
if st.button('**Predict**', disabled=button_disabled):
    # predict
    try:
        # extract features
        input_df = extract_features(input_df)

        # Get probabilities
        # probabilities format: [[prob_stay, prob_churn]]
        probs = model.predict_proba(input_df)
        
        # Extract only the churn probability (class 1)
        # We use .item() or [0, 1] to get the actual float number
        churn_prob = probs[0, 1] 

        # Determine label (compare scalar to scalar)
        is_churn = churn_prob >= threshold
        pred_label = 1 if is_churn else 0

        st.divider()
        
        # --- Display Results ---
        if pred_label == 1:
            st.error("### Result: High Risk of Churn")
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric(label="Churn Probability Score", value=f"{churn_prob:.2%}")
            with col2:
                st.info("💡 **Risk Analysis:** This employee shows patterns similar to those who have resigned in the past.")
            
            strategy_recs(pred_label, churn_prob, inputs)
        else:
            st.success("### Result: Likely to Stay")
            st.metric(label="Churn Probability Score", value=f"{churn_prob:.2%}")
            strategy_recs(pred_label, churn_prob, inputs)

    except Exception as e:
        st.error(f"Error during prediction: {e}")
