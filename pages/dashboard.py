# import library
import pandas as pd
import numpy as np
import math

import plotly.express as px
import plotly.graph_objects as go

import streamlit as st

from utils import extract_features

# load data
@st.cache_data
def load_data():
    # Ganti dengan path file kamu
    df = pd.read_csv('data/employee_churn_prediction_updated.csv')
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# load css
def read_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}<style>", unsafe_allow_html=True)
read_css('style.css')

# extract features
df = extract_features(df)

df['unachieved_target_category'] = pd.cut(
    df['unachieved_target'],
    bins=[-float('inf'), -0.01, 0.0, 20.0, 50.0, float('inf')],
    labels=[
        "Exceeded Target (< 0)", 
        "On Track (0)", 
        "Low (1 - 20)", 
        "Medium (21 - 50)", 
        "High (> 50)"
    ],
    include_lowest=True
)

df['overtime_ratio_category'] = pd.cut(
    df['overtime_ratio'],
    bins=[-float('inf'), 0.0, 0.15, 0.30, float('inf')],
    labels=[
        "No Overtime (0%)", 
        "Low (< 15%)", 
        "Medium (15%-30%)", 
        "High (> 30%)"
    ],
    include_lowest=True
)

df['unachieved_target_category'] = df['unachieved_target_category'].astype(str)
df['overtime_ratio_category'] = df['overtime_ratio_category'].astype(str)
df['churn'] = df['churn'].map({0: "Stayed", 1: "Churned"})

# title
st.title('TalentPulse: Employee Churn Prediction for HR')
st.markdown("This dashboard is a showcase of employee turnover analysis, demonstrating how to monitor retention rates and identify key churn risk factors using real-world enterprise data.")
st.divider()

# reset filter
def reset_filters():
    st.session_state.churn_filter = []
    st.session_state.job_satisfaction_filter = []
    st.session_state.manager_support_filter = []
    st.session_state.distance_group_filter = []
    st.session_state.unachieved_target_filter = []
    st.session_state.overtime_ratio_filter = []

# filter
with st.sidebar:
    st.title(':material/filter_alt: **Filter**')
    # churn
    list_churn = df['churn'].unique().tolist()
    selected_churn = st.multiselect(
        "**Status**",
        options=list_churn,
        default=[],
        placeholder="Choose options",
        key="churn_filter"
    )
    if not selected_churn:
        selected_churn = list_churn

    # unachievement target
    list_unachieved = [
        "Exceeded Target (< 0)", 
        "On Track (0)", 
        "Low (1 - 20)", 
        "Medium (21 - 50)", 
        "High (> 50)"]
    selected_unachieved_target = st.multiselect(
        "**Unachieved Target**",
        options=list_unachieved,
        default=[],
        placeholder="Choose options",
        key="unachieved_target_filter"
    )
    if not selected_unachieved_target:
        selected_unachieved_target = list_unachieved

    # overtime ratio
    list_overtime = [
        "No Overtime (0%)", 
        "Low (< 15%)", 
        "Medium (15%-30%)", 
        "High (> 30%)"]
    selected_overtime_ratio = st.multiselect(
        "**Overtime Ratio**",
        options=list_overtime,
        default=[],
        placeholder="Choose options",
        key="overtime_ratio_filter"
    )
    if not selected_overtime_ratio:
        selected_overtime_ratio = list_overtime

    # job satisfaction
    selected_job_satisfaction = st.multiselect(
        "**Job Satisfaction**",
        options=[1,2,3,4],
        default=[],
        placeholder="Choose options",
        key="job_satisfaction_filter"
    )
    if not selected_job_satisfaction:
        selected_job_satisfaction = [1,2,3,4]

    # manager support score
    selected_manager_support_score = st.multiselect(
        "**Manager Support Score**",
        options=[1,2,3,4],
        default=[],
        placeholder="Choose options",
        key="manager_support_filter"
    )
    if not selected_manager_support_score:
        selected_manager_support_score = [1,2,3,4]

    # distance group
    list_distance_group = [
        "Near",
        "Medium",
        "Far"
    ]
    selected_distance_group = st.multiselect(
        "**Distance Group**",
        options=list_distance_group,
        default=[],
        placeholder="Choose options",
        key="distance_group_filter"
    )
    if not selected_distance_group:
        selected_distance_group= list_distance_group

    # reset filter button
    st.button(
    ":material/filter_alt_off: **Reset Filters**",
    on_click=reset_filters
)

# apply filter
df_filtered = df[
    (df["churn"].isin(selected_churn)) &
    (df["unachieved_target_category"].isin(selected_unachieved_target)) &
    (df["overtime_ratio_category"].isin(selected_overtime_ratio)) &
    (df["job_satisfaction"].isin(selected_job_satisfaction)) &
    (df["manager_support_score"].isin(selected_manager_support_score)) &
    (df["distance_group"].isin(selected_distance_group))
]



# Dashboard
# 1: KPI Metrics
total_emp = len(df_filtered)
total_churn = len(df_filtered[df_filtered['churn'] == "Churned"])
churn_rate = (len(df_filtered[df_filtered['churn'] == "Stayed"]) / total_emp * 100) if total_emp > 0 else 0
avg_churn_tenure = (
    df_filtered[df_filtered["churn"] == "Churned"]
    ["company_tenure_years"]
    .mean()
)

m1, m2, m3, m4 = st.columns(4, gap="medium")
with m1:
    with st.container(border=True):
        col1, col2 = st.columns([1,3])
        with col1:
            st.title(":material/group:")
        with col2:
            st.metric(
                "Total Employees", 
                f"{total_emp}"
            )
with m2:
    with st.container(border=True):
        col1, col2 = st.columns([1,3])
        with col1:
            st.title(":material/person_remove:")
        with col2:
            st.metric(
                "Total Churn", 
                f"{total_churn}"
            )

with m3:
    with st.container(border=True):
        col1, col2 = st.columns([1,3])
        with col1:
            st.title(":material/percent:")
        with col2:
            st.metric(
                "Churn Rate",
                f"{100 - churn_rate:.1f}%",
            )

with m4:
    with st.container(border=True):
        col1, col2 = st.columns([1,3])
        with col1:
            st.title(":material/schedule:")
        with col2:
            st.metric(
                "Avg Years Churn Tenure",
                f"{avg_churn_tenure:.2f}"
            )


df_plot = df_filtered.copy()


# 2: main visualization
st.subheader("👥 Employees Demographic Profile")
st.caption("Breaks down the core characteristics of the workforce, analyzing how gender distribution, education level, work location, and marital status correlate with employee turnover trends.")

# initials
color_discrete_map= {
    'Stayed': '#636EFA', 
    'Churned': '#EF553B'
}
title={
    'y': 0.98,
    'x': 0.5,
    'xanchor': 'center',
    'yanchor': 'top'
}

legend= dict(
    title_text="",
    orientation="h",
    yanchor="bottom",
    y=1.05,
    xanchor="center",
    x=0.35
)



col1, col2, col3, col4 = st.columns(4)

# gender
with col1:
    with st.container(border=True):
        fig = px.histogram(
            df_plot, 
            x="gender", 
            color="churn", 
            barmode="group",
            labels={"gender": "Gender", "count": "Number of Employees"},
            color_discrete_map=color_discrete_map,
            title="Churn Distribution by Gender"
        )
        # fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        fig.update_layout(legend=legend, title=title)
        st.plotly_chart(fig, use_container_width=True)

# education
with col2:
    with st.container(border=True):
        fig = px.histogram(
            df_plot, 
            x="education", 
            color="churn", 
            barmode="group",
            category_orders={"education": sorted(df_plot['education'].unique().tolist())},
            labels={"education": "Education Level"},
            color_discrete_map=color_discrete_map,
            title="Churn Distribution by Education Level"
        )
        fig.update_layout(legend=legend, title=title)
        st.plotly_chart(fig, use_container_width=True)

# work location
with col3:
    with st.container(border=True):
        fig = px.histogram(
            df_plot, 
            x="work_location", 
            color="churn", 
            barmode="group",
            labels={"work_location": "Work Location"},
            color_discrete_map=color_discrete_map,
            title="Churn Distribution by Work Location"
        )
        fig.update_layout(legend=legend, title=title)
        st.plotly_chart(fig, use_container_width=True)

# marital status
with col4:
    with st.container(border=True):
        fig = px.histogram(
            df_plot, 
            x="marital_status", 
            color="churn", 
            barmode="group",
            labels={"marital_status": "Marital Status"},
            color_discrete_map=color_discrete_map,
            title="Churn Distribution by Marital Status"
        )
        fig.update_layout(legend=legend, title=title)
        st.plotly_chart(fig, use_container_width=True)


# section 3
st.subheader("📈 Performance & Workload")
st.caption("evaluates the employee's direct workplace footprint, analyzing the relationship between sales target achievements, accumulated weekly overtime, and their overall impact on organizational turnover.")

legend= dict(
    title_text="",
    orientation="h",
    yanchor="bottom",
    y=1.05,
    xanchor="center",
    x=0.45
)
col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        fig = px.histogram(
            df_plot,
            x='unachieved_target',
            color='churn',
            labels={'unachieved_target': 'Unachieved Target'},
            color_discrete_map=color_discrete_map,
            title="Distribution of Unachivement Target",
        )
        fig.update_layout(legend=legend, title=title, yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
with col2:
    with st.container(border=True):
        fig = px.histogram(
            df_plot,
            x='overtime_ratio',
            color='churn',
            labels={'overtime_ratio': 'Overtime Ratio'},
            color_discrete_map=color_discrete_map,
            title="Distribution of Overtime Ratio",
        )
        fig.update_layout(legend=legend, title=title, yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)


st.subheader("🚗 Environment & Logistics")
st.caption("Explores the daily lifestyle and psychological catalysts behind attrition, highlighting how commuting distances, direct manager support, and overall job satisfaction scores influence an employee's decision to stay or leave.")

legend= dict(
    title_text="",
    orientation="h",
    yanchor="bottom",
    y=1,
    xanchor="center",
    x=0.4
)
col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        fig = px.box(
            df_plot,
            x="churn",
            y="distance_to_office_km", 
            color="churn",
            color_discrete_map=color_discrete_map,
            title="Commuting Distance Impact",
            labels={
                "churn": "Churn",
                "distance_to_office_km": "Distance to Office (KM)"
            }
        )
        fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), title=title, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    with st.container(border=True):
        df_job = df_plot.groupby(['job_satisfaction', 'churn'])['churn'].count().reset_index(name='Employee Count')
        fig = px.bar(
            df_job,
            x="job_satisfaction",
            y="Employee Count",
            color="churn",
            color_discrete_map=color_discrete_map,
            title="Job Satisfaction Distribution",
            barmode="stack",
            text="Employee Count",
            labels={
                "job_satisfaction": "Job Satisfaction",
                "Employee Count": "Employee Count",
                "churn": "Status"
            }
        )
        fig.update_layout(
            title=title,
            xaxis= dict(tickmode="linear", tick0=1, dtick=1),
            legend= legend,
            margin= dict(l=10, r=10, t=60, b=10)
        )
        fig.update_traces(texttemplate='%{text}', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)

with col3:
    with st.container(border=True):
        df_manager = df_plot.groupby(['manager_support_score', 'churn'])['churn'].count().reset_index(name='Employee Count')
        fig = px.bar(
            df_manager,
            x="manager_support_score",
            y="Employee Count",
            color="churn",
            color_discrete_map=color_discrete_map,
            title="Manager Support Score Distribution",
            barmode="stack",
            text="Employee Count",
            labels={
                "manager_support_score": "Manager Support Score",
                "Employee Count": "Employee Count",
                "churn": "Status"
            }
        )
        fig.update_layout(
            title=title,
            xaxis= dict(tickmode="linear", tick0=1, dtick=1),
            legend= legend,
            margin= dict(l=10, r=10, t=60, b=10)
        )
        fig.update_traces(texttemplate='%{text}', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)