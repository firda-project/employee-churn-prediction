# import library
import streamlit as st

# navigation
dashboard = st.Page(
    'pages/dashboard.py',
    title= 'Dashboard'
)
nav = {
    "Overview": [
        st.Page('pages/dashboard.py', title='Dashboard', icon="📊")
    ],
    "Prediction": [
        st.Page(
            'pages/predict_single.py',
            title='Single Prediction',
            icon="👤"
        ),
        st.Page(
            'pages/predict_batch.py',
            title='Batch Prediction',
            icon="📁"
        )
    ]
}

pg = st.navigation(nav)
st.set_page_config(
    page_title='Turnover Analysis',
    layout="wide"
)
pg.run()
