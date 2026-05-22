# import library
import pandas as pd
import numpy as np
from io import BytesIO
from openpyxl.styles import Alignment

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

# load css
def read_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}<style>", unsafe_allow_html=True)

read_css('style.css')


# data description
desc = {
    "Column_Name": [
        'monthly_target',
        'target_achievement',
        'working_hours_per_week',
        'overtime_hours_per_week',
        'job_satisfaction',
        'manager_support_score',
        'distance_to_office_km'
    ],
    "Data_Type": [
        'Integer',
        'Float',
        'Integer',
        'Integer',
        'Integer',
        'Integer',
        'Integer'
    ],
    "Range/Example": [
        'e.g. 50, 100, 200',
        'e.g. 0.85',
        'e.g. 55',
        'e.g. 10',
        '1 to 4',
        '1 to 4',
        'e.g. 5, 10, 20'
    ],
    "Description": [
        'The performance target assigned to the employee for the month.',
        'The percentage of the monthly target successfully achieved by the employee.',
        'The total number of standard or contracted hours an employee is expected to work in a typical week.',
        'The number of additional hours worked per week beyond the standard or contracted working hours.',
        "Employee's job satisfaction score (1: Lowest, 4: Highest).",
        'Score reflecting the support received from their direct manager (1: Lowest, 4: Highest).',
        "The distance from the employee's residence to the office in kilometers."
    ]
}
data_desc = pd.DataFrame(desc)


# template file dataset
template_data = pd.DataFrame(columns=[
    'monthly_target',
    'target_achievement',
    'working_hours_per_week',
    'overtime_hours_per_week',
    'job_satisfaction',
    'manager_support_score',
    'distance_to_office_km'
])
template_data.loc[0] = [100, 0.85, 55, 10, 3, 4, 12]

@st.cache_data
def export_to_excel(
    _df,
    sheet_name="Sheet1",
    wrap_columns=None
):

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        _df.to_excel(
            writer,
            index=False,
            sheet_name=sheet_name
        )

        worksheet = writer.sheets[sheet_name]

        wrap_col_indexes = []

        # index wrap columns
        if wrap_columns:
            wrap_col_indexes = [
                _df.columns.get_loc(col) + 1
                for col in wrap_columns
            ]

        # Styling cell
        for row in worksheet.iter_rows():

            for cell in row:

                # vertical top
                cell.alignment = Alignment(
                    vertical="top"
                )

                # Wrap text
                if cell.column in wrap_col_indexes:

                    cell.alignment = Alignment(
                        wrap_text=True,
                        vertical="top"
                    )

        # Auto width column
        for column_cells in worksheet.columns:

            length = max(
                len(str(cell.value)) if cell.value else 0
                for cell in column_cells
            )

            worksheet.column_dimensions[
                column_cells[0].column_letter
            ].width = min(length + 5, 70)

    # Reset pointer
    output.seek(0)

    return output


# func check data format
def data_prep(X):
    cleaned_df = X.copy()
    warnings = []

    # list columns
    columns = [
        'monthly_target',
        'target_achievement',
        'working_hours_per_week',
        'overtime_hours_per_week',
        'job_satisfaction',
        'manager_support_score',
        'distance_to_office_km'
    ]

    # check completed columns
    missing_cols = [col for col in columns if col not in cleaned_df.columns]
    if missing_cols:
        warnings.append(f"❌ **Missing Columns:** The file is missing required columns: {', '.join(missing_cols)}.")
        return cleaned_df, warnings

    # cek missing
    initial_missing = cleaned_df[columns].isna().sum()
    total_initial_missing = initial_missing.sum()
    
    if total_initial_missing > 0:
        details = [f"**{col}**: {count} missing" for col, count in initial_missing.items() if count > 0]
        warnings.append(f"⚠️ **Initial Missing Values:** Found original missing values in your file: {', '.join(details)}.")

    # target achievement
    if 'target_achievement' in cleaned_df.columns:
        # change to be string type
        target_str = cleaned_df['target_achievement'].astype(str).str.strip()

        # check values using (,)
        if target_str.str.contains(',').any():
            cleaned_df['target_achievement'] = target_str.str.replace(',', '.', regex=False)

        # check values without (,) or (.)
        try:
            temp_float = cleaned_df['target_achievement'].astype(float)
            if ((temp_float > 1.0) & (temp_float % 1 == 0)).any():
                warnings.append("⚠️ **Format Warning (Target Achievement):** Found values greater than 1 without decimals (e.g., 85 instead of 0.85). Please use decimal format between 0.0 and 1.0.")
        except ValueError:
            warnings.append("❌ **Format Error (Target Achievement):** Contains non-numeric text that cannot be converted.")

    # data type must be numeric
    for col in columns:
        if not pd.api.types.is_numeric_dtype(cleaned_df[col]):
            try:
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
                post_missing_count = cleaned_df.isna().sum()
                pre_missing_count = initial_missing[col]

                if post_missing_count > pre_missing_count:
                    added_missing = post_missing_count - pre_missing_count
                    warnings.append(
                        f"❌ **Data Type Corruption ({col}):** {added_missing} row(s) contained non-numeric text "
                        f"(e.g., letters or special symbols) and were forced into empty values (**NaN**). Please fix these rows."
                    )
            except Exception:
                warnings.append(f"❌ **Data Type Error ({col}):** Failed to convert column to numeric data type.")

    # validate range values
    score_cols = ['job_satisfaction', 'manager_support_score']
    for col in score_cols:
        if col in cleaned_df.columns:
            # Find the rows where the values are < 1 or > 4 (ignore NaN to avoid errors)
            invalid_rows = cleaned_df[(cleaned_df[col] < 1) | (cleaned_df[col] > 4)]
            
            if not invalid_rows.empty:
                invalid_values = invalid_rows[col].dropna().unique()
                warnings.append(
                    f"⚠️ **Out of Range ({col}):** Found invalid scores {list(invalid_values)}. "
                    f"The score must be an integer between **1 and 4** (1: Lowest, 4: Highest)."
                )
    return cleaned_df, warnings


# create data to match the training data format during modeling
def data_complete (X):
    complete_data = X.copy()

    # list columns
    list_columns = [
        'age', 'gender', 'education', 'experience_years', 'monthly_target',
        'target_achievement', 'working_hours_per_week', 'overtime_hours_per_week',
        'salary', 'commission_rate', 'job_satisfaction', 'work_location',
        'manager_support_score', 'company_tenure_years', 'marital_status',
        'distance_to_office_km'
    ]

    # add columns
    for col in list_columns:
        if col not in complete_data.columns:
            complete_data[col] = np.nan
    
    complete_data = complete_data.reindex(columns=list_columns)
    
    return complete_data



# title
st.title('Batch Employee Churn Prediction')
st.markdown("Multi-employee retention risk assessment powered by quick and bulk .csv or .xlsx data uploads.")
st.divider()

# Predict Guide
# step 1
st.subheader("Step 1: Prepare Your Data")

st.markdown("To ensure accurate predictions, please format your dataset according to the specifications above!")
st.table(data_desc)

st.markdown("Alternatively, you can download our pre-formatted template, fill in your employee data, and upload it back here!")
template_excel = export_to_excel(
    _df= template_data,
    sheet_name="Template")

st.download_button(
    label="📥 **Download Excel Template**",
    data=template_excel,
    file_name="employee_churn_template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)



st.subheader("Step 2: Upload File")
uploaded_file = st.file_uploader(
    "Upload your CSV or Excel file", 
    type=["csv", "xlsx"]
)
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            input_df = pd.read_csv(uploaded_file)
        else:
            input_df = pd.read_excel(uploaded_file)
    # preprocessing
        cleaned_df, validation_warnings = data_prep(input_df)
    except Exception as e:
        st.error(f"Error reading file: {e}")

    # display warning
    if validation_warnings:
        st.subheader("⚠️ Data Quality Issues Found")
        for warning in validation_warnings:
            st.markdown(warning)
            
        # Action choices: Continue if it's just a warning, or stop if there is an 'Error'
        # Here we check if the word 'Error' is present in the list of warnings
        # has_critical_error = any("Error" in w for w in validation_warnings)
        has_critical_error = any("❌" in w for w in validation_warnings)
        
        if has_critical_error:
            st.error("🛑 Prediction halted. Please fix the critical formatting errors listed above and re-upload.")
            st.stop() # Hentikan proses eksekusi ke model
        else:
            st.warning("You can still proceed, but the results might be inaccurate due to the issues above.")
    else:
        st.success("✅ Your data is complete and in accordance with the format. Click 'Run Bulk Prediction' to view the results.")
        button_disabled = False

    # completing data
    completed_df = data_complete(cleaned_df)
    
    # feature engineering
    final_df = extract_features(completed_df)
    
    # predict
    st.subheader("Step 3: Run Bulk Prediction")
    if st.button("**Run Bulk Prediction**", disabled=button_disabled):
        try:
            # predict
            probs = model.predict_proba(final_df)
            churn_prob = probs[:, 1]

            results_df = input_df.copy()
            results_df['churn_probability'] = churn_prob
            results_df = get_recommendations(results_df)
            results_df = results_df.map(lambda x: x.replace('**', '')  if isinstance(x, str) else x)

            st.markdown("🎉 **Prediction Results**")
            # Replace the \n with an HTML linebreak
            df = results_df.map(lambda x: x.replace('\n', '<br>') if isinstance(x, str) else x)

            # Show as a static table
            table_html = f"""
            <div class="table-container">
                {df.head(5).to_html(escape=False)}
            </div>
            """
            st.markdown(table_html, unsafe_allow_html=True)
            
            # download file result
            st.subheader("Step 4: Get The Results")
            st.markdown("You can click **'Download The Results'** to get the results.")
            excel_result = export_to_excel(
                _df=results_df,
                sheet_name="Churn_Result",
                wrap_columns=['recommendations']
            )
            
            st.download_button(
                label="📥 **Download Excel Result**",
                data=excel_result,
                file_name="employee_churn_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Prediction failed: {e}")
    pass
