import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    layout="wide",
    page_title="IMVED Employee Analytics Dashboard",
    page_icon="🧑‍💻"
)

st.markdown("""
<style>
    /* Apply a vibrant background gradient to the entire page */
    body {
        background-image: linear-gradient(to right top, #051937, #004d7a, #008793, #00bf72, #a8eb12);
        background-attachment: fixed;
    }

    /* Make the main content area transparent to show the gradient */
    div[data-testid="stAppViewContainer"] > .main {
        background-color: transparent;
    }
    
    /* Style the sidebar with a dim, semi-transparent look */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Main title style */
    .main-title {
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        color: #FFFFFF; /* White color for better contrast on gradient */
        padding: 20px 0;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.6);
    }
    
    /* Style for metric cards using a dimmer glassmorphism effect */
    [data-testid="stMetric"] {
        background: rgba(0, 0, 0, 0.4); /* Darker semi-transparent black */
        backdrop-filter: blur(12px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        color: white;
    }

    /* Make metric labels and values white */
    [data-testid="stMetric"] label, [data-testid="stMetric"] div {
        color: white;
    }

    /* Style for containers holding charts (dim glassmorphism) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(0, 0, 0, 0.25); /* Dimmer background */
        backdrop-filter: blur(12px);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    /* General headers and subheaders style */
    h1, h2, h3 {
        color: #FFFFFF;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.5);
    }

    /* Add some space between tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    
    /* Style for tabs to make them more visible */
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(0,0,0,0.2);
        border-radius: 8px;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #008793; /* A color from our gradient */
    }

</style>
""", unsafe_allow_html=True)


# --- Data Loading ---
# The caching decorator helps in loading data faster after the first run.
@st.cache_data
def load_data(file_path):
    """Loads data from a CSV file and handles potential errors."""
    try:
        df = pd.read_csv(file_path)
        # Convert 'Attrition' to a more usable format if needed (e.g., 1 for Yes, 0 for No)
        df['AttritionNumeric'] = df['Attrition'].apply(lambda x: 1 if x == 'Yes' else 0)
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found.")
        st.info("Please ensure the CSV file is in the same directory as the script.")
        return None

# Load the dataset
df = load_data("mock_imved_tech_data.csv")

# If data loading fails, stop the app execution.
if df is None:
    st.stop()

# --- Main Page Title ---
st.markdown('<p class="main-title">🧑‍💻 IMVED Technologies Employee Analytics</p>', unsafe_allow_html=True)


# --- Sidebar for Filters ---
with st.sidebar:
    st.header("🔍 Filter Options")

    # Reset Filters Button
    if st.button("Reset All Filters"):
        st.session_state.selected_departments = df['Department'].unique().tolist()
        st.session_state.selected_cities = df['City'].unique().tolist()
        st.session_state.selected_exp = (int(df['YearsOfExperience'].min()), int(df['YearsOfExperience'].max()))
        st.experimental_rerun() # Rerun the script to apply reset state

    # Initialize session state for filters if they don't exist
    if 'selected_departments' not in st.session_state:
        st.session_state.selected_departments = df['Department'].unique().tolist()
    if 'selected_cities' not in st.session_state:
        st.session_state.selected_cities = df['City'].unique().tolist()
    if 'selected_exp' not in st.session_state:
        st.session_state.selected_exp = (int(df['YearsOfExperience'].min()), int(df['YearsOfExperience'].max()))

    # Multiselect for Department
    selected_departments = st.multiselect(
        "Select Department",
        options=df['Department'].unique(),
        key='selected_departments'
    )

    # Multiselect for City
    selected_cities = st.multiselect(
        "Select City",
        options=df['City'].unique(),
        key='selected_cities'
    )

    # Slider for Years of Experience
    min_exp, max_exp = int(df['YearsOfExperience'].min()), int(df['YearsOfExperience'].max())
    selected_exp = st.slider(
        "Filter by Years of Experience",
        min_exp, max_exp,
        key='selected_exp'
    )

# Filter the DataFrame based on selections
filtered_df = df[
    (df['Department'].isin(selected_departments)) &
    (df['City'].isin(selected_cities)) &
    (df['YearsOfExperience'].between(selected_exp[0], selected_exp[1]))
]

# --- Key Metrics (KPIs) ---
st.header("📊 Key Performance Indicators")
total_employees = filtered_df.shape[0]
attrition_count = filtered_df[filtered_df['Attrition'] == 'Yes'].shape[0]
attrition_rate = (attrition_count / total_employees) * 100 if total_employees > 0 else 0
avg_salary = filtered_df['SalaryINR'].mean()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Employees", f"{total_employees}", delta_color="off")
with col2:
    st.metric("Attrition Rate", f"{attrition_rate:.2f}%", help="Percentage of employees who left the company.")
with col3:
    st.metric("Average Salary (INR)", f"₹ {avg_salary:,.0f}")

st.markdown("---", unsafe_allow_html=True)


# --- Using Tabs for Cleaner Navigation ---
tab1, tab2, tab3 = st.tabs([
    "🏢 **Department & Role Insights**",
    "🧑‍💼 **Demographics & Salary**",
    "📈 **Correlation Analysis**"
])

# --- Tab 1: Department & Role Insights ---
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("Attrition by Department")
            attrition_dept = filtered_df.groupby(['Department', 'Attrition']).size().reset_index(name='count')
            fig_attr_dept = px.bar(
                attrition_dept, x='Department', y='count', color='Attrition',
                title="Attrition Count by Department", barmode='group',
                color_discrete_map={'Yes': '#FF6B6B', 'No': '#6BCB77'},
                labels={'count': 'Number of Employees', 'Department': 'Department'}
            )
            fig_attr_dept.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_attr_dept, use_container_width=True)

    with col2:
        with st.container(border=True):
            st.subheader("Job Roles in Technology Dept.")
            tech_df = filtered_df[filtered_df['Department'] == 'Technology']
            if not tech_df.empty:
                role_counts = tech_df['JobRole'].value_counts().reset_index()
                role_counts.columns = ['JobRole', 'count']
                fig_roles = px.bar(
                    role_counts.sort_values(by='count'), y='JobRole', x='count', orientation='h',
                    title="Number of Employees by Job Role (Technology)",
                    color='JobRole',
                    labels={'count': 'Number of Employees', 'JobRole': 'Job Role'}
                )
                fig_roles.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                st.plotly_chart(fig_roles, use_container_width=True)
            else:
                st.info("No data available for the Technology department with the current filters.")


# --- Tab 2: Demographics & Salary ---
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("Gender Distribution")
            gender_counts = filtered_df['Gender'].value_counts().reset_index()
            gender_counts.columns = ['Gender', 'count']
            fig_gender = px.pie(
                gender_counts, names='Gender', values='count',
                title='Employee Gender Distribution', hole=0.4,
                color_discrete_map={'Male': '#66b3ff', 'Female': '#ff9999'}
            )
            fig_gender.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_gender, use_container_width=True)

    with col2:
        with st.container(border=True):
            st.subheader("Salary Distribution")
            fig_salary = px.histogram(
                filtered_df, x='SalaryINR', nbins=30,
                title="Employee Salary Distribution",
                labels={'SalaryINR': 'Salary (INR)'},
                color_discrete_sequence=['#4a90e2']
            )
            fig_salary.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_salary, use_container_width=True)

    # New Interactive Scatter Plot
    with st.container(border=True):
        st.subheader("Salary vs. Years of Experience")
        fig_salary_exp = px.scatter(
            filtered_df,
            x='YearsOfExperience',
            y='SalaryINR',
            color='Department',
            hover_data=['JobRole', 'City'],
            title='Salary vs. Experience by Department',
            labels={'YearsOfExperience': 'Years of Experience', 'SalaryINR': 'Salary (INR)'}
        )
        fig_salary_exp.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_salary_exp, use_container_width=True)


# --- Tab 3: Correlation Analysis ---
with tab3:
    with st.container(border=True):
        st.subheader("Correlation Between Numerical Features")
        numerical_cols = filtered_df.select_dtypes(include=np.number)

        # Let user select which columns to include in the heatmap
        selected_cols = st.multiselect(
            "Select features for correlation heatmap:",
            options=numerical_cols.columns,
            default=[col for col in numerical_cols.columns if col not in ['EmployeeID', 'AttritionNumeric']]
        )

        if selected_cols:
            corr = numerical_cols[selected_cols].corr()
            fig_corr = px.imshow(
                corr, text_auto=True, aspect="auto",
                title="Correlation Heatmap",
                color_continuous_scale='RdYlGn' # Red-Yellow-Green scale
            )
            fig_corr.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.warning("Please select at least one feature to display the heatmap.")


# --- Raw Data Display in an Expander ---
with st.expander("⬇️ View and Download Raw Data"):
    st.subheader("Filtered Employee Data")
    st.dataframe(filtered_df)

    # Function to convert dataframe to CSV for download
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df_to_csv(filtered_df)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='filtered_employee_data.csv',
        mime='text/csv',
    )
