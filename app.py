import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="EduPro Analytics Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .kpi-card {
        background: linear-gradient(135deg, #1e2130, #2a2d3e);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #4f8ef7;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .kpi-label {
        color: #a0aec0;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .kpi-value {
        color: #ffffff;
        font-size: 32px;
        font-weight: 800;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    xls = pd.ExcelFile("project dashboard.xlsx")
    users        = pd.read_excel(xls, "users").drop_duplicates(subset="UserID")
    courses      = pd.read_excel(xls, "courses").drop_duplicates(subset="CourseID")
    transactions = pd.read_excel(xls, "transations").drop_duplicates()
    teachers     = pd.read_excel(xls, "Teachers").drop_duplicates(subset="TeacherID")

    transactions["TransactionDate"] = pd.to_datetime(transactions["TransactionDate"])
    transactions["Year"]  = transactions["TransactionDate"].dt.year
    transactions["YearMonth"] = transactions["TransactionDate"].dt.to_period("M").astype(str)

    df = (transactions
          .merge(users,    on="UserID")
          .merge(courses,  on="CourseID")
          .merge(teachers, on="TeacherID"))
    
    df.columns = df.columns.str.strip()
    return df

with st.spinner("Loading data..."):
    df = load_data()

# -----------------------------
# SIDEBAR FILTERS (Safe Checks)
# -----------------------------
with st.sidebar:
    st.markdown("## 🔍 Filters")
    
    age_opts = sorted(df["Age"].unique()) if "Age" in df.columns else []
    age_filter = st.multiselect("👤 Age", options=age_opts, default=age_opts)

    gen_opts = df["Gender"].unique() if "Gender" in df.columns else []
    gender_filter = st.multiselect("⚥ Gender", options=gen_opts, default=gen_opts)

    cat_opts = sorted(df["CourseCategory"].unique()) if "CourseCategory" in df.columns else []
    category_filter = st.multiselect("📚 Course Category", options=cat_opts, default=cat_opts)

# -----------------------------
# APPLY FILTERS (Conditional)
# -----------------------------
filtered_df = df.copy()
if "Age" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Age"].isin(age_filter)]
if "Gender" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Gender"].isin(gender_filter)]
if "CourseCategory" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["CourseCategory"].isin(category_filter)]

# -----------------------------
# KPIs
# -----------------------------
k1, k2, k3 = st.columns(3)
active_users = filtered_df["UserID"].nunique() if "UserID" in filtered_df.columns else 0
total_courses = filtered_df["CourseID"].nunique() if "CourseID" in filtered_df.columns else 0

with k1:
    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Active Users</div><div class='kpi-value'>{active_users}</div></div>", unsafe_allow_html=True)
with k2:
    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Total Courses</div><div class='kpi-value'>{total_courses}</div></div>", unsafe_allow_html=True)

# -----------------------------
# CHARTS (Fixing line 202 error)
# -----------------------------
st.markdown("### 📋 Overview")
col1, col2 = st.columns(2)

with col1:
    # Safe check for Age column before plotting
    if "Age" in filtered_df.columns:
        age_data = filtered_df.groupby("Age")["UserID"].nunique().reset_index()
        fig1 = px.bar(age_data, x="UserID", y="Age", orientation="h", title="Enrollments by Age", template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Age data not available in the current view.")

with col2:
    if "Gender" in filtered_df.columns:
        gen_data = filtered_df.groupby("Gender")["UserID"].nunique().reset_index()
        fig2 = px.pie(gen_data, names="Gender", values="UserID", title="Gender Ratio", template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)
