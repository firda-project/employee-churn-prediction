import pandas as pd

# feature engineering
def extract_features(X):
    new_df = X.copy()

    # Feature Extraction
    # Overtime Ratio
    new_df['overtime_ratio'] = new_df['overtime_hours_per_week'] / new_df['working_hours_per_week']

    # Overall Satisfaction
    new_df['overall_satisfaction'] = new_df['job_satisfaction'] * new_df['manager_support_score']
    
    # Unachieved Target
    new_df['unachieved_target'] = new_df['monthly_target'] * (1 - new_df['target_achievement'])
    
    # Distance Group
    new_df['distance_group'] = pd.cut(
        new_df['distance_to_office_km'],
        bins=[0,10,25,50],
        labels=['Near','Medium','Far']
    )

    return new_df

def recs_prob(row):
    if 0.4 < row['churn_probability'] <= 0.6:
        return [
            "- **Early Check-in:** Schedule a one-on-one session to understand current workload and concerns before dissatisfaction escalates.",
            "- **Recognition & Visibility:** Acknowledge recent contributions publicly to reinforce sense of belonging and value.",
            "- **Career Path Discussion:** Initiate a conversation about growth opportunities, skill development, or role expansion within the company.",
        ]
    elif 0.6 < row['churn_probability'] <= 0.8:
        return [
            "- **Structured Retention Interview:** Conduct a formal stay interview to identify specific pain points — focus on workload, manager relationship, and job satisfaction.",
            "- **Workload Review:** Assess weekly working hours and overtime ratio; consider redistributing tasks or adjusting targets if overload is confirmed.",
            "- **Manager Coaching:** Flag this employee's manager for a support quality review, especially if manager_support_score is below 3.",
        ]
    elif row['churn_probability'] > 0.8:
        return [
            "- **Immediate Escalation:** Escalate to HR lead or direct manager — delay significantly reduces retention probability at this risk level.",
            "- **Retention Package Review:** Evaluate whether a role adjustment, flexible work arrangement, or compensation review is feasible and justified.",
            "- **Exit Risk Documentation:** If retention fails, initiate knowledge transfer planning to minimize operational disruption.",
        ]
    else:
        return [
            "- **Recognition Program:** Acknowledge their consistency to maintain high motivation.",
            "- **Career Development:** Discuss potential leadership tracks or new skill certifications.",
            "- **Mentorship Role:** Consider assigning them as a mentor for new hires."
        ]

def recs_features(row):
    recs_list = []
    if row['job_satisfaction'] <= 2:
        recs_list.append("- **Improve Work Environment:** Conduct a 1-on-1 feedback session.")
    if row['manager_support_score'] <= 2:
        recs_list.append("- **Managerial Intervention:** Coaching for the direct supervisor.")
    if row['target_achievement'] < 0.5:
        recs_list.append("- **Performance Support:** Review target realism and offer technical training.")
    if row['distance_to_office_km'] > 25:
        recs_list.append("- **Flexible Work:** Consider remote work options.")
    
    if not recs_list:
        recs_list.append("- **Stay Interview:** Proactively engage with the employee to understand their long-term career goals.")
    
    return recs_list

def combine_recs(row):
    prob_list = recs_prob(row)
    feat_list = recs_features(row)
    
    # merge list
    total_recs = prob_list + feat_list
    return "\n".join(total_recs)

def get_recommendations(data):
    if isinstance(data, pd.DataFrame):
        df_result = data.copy()
        df_result['recommendations'] = df_result.apply(combine_recs, axis=1)
        return df_result
    else:
        if isinstance(data, dict):
            row_data = pd.Series(data)
        else:
            row_data = data
        return {
            'recommendations': combine_recs(row_data)
        }