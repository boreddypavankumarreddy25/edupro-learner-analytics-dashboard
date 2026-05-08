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
    .insight-card {
        background: linear-gradient(135deg, #1a1f36, #2d3561);
        border-radius: 10px;
        padding: 15px 20px;
        margin: 8px 0;
        border-left: 4px solid #48bb78;
        color: #e2e8f0;
        font-size: 15px;
    }
    .section-title {
        color: #e2e8f0;
        font-size: 20px;
        font-weight: 700;
        margin: 20px 0 10px 0;
        padding-bottom: 6px;
        border-bottom: 2px solid #4f8ef7;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
<div style='background: linear-gradient(135deg, #1a1f36, #2d3561);
     padding: 25px 30px; border-radius: 15px; margin-bottom: 20px;
     border: 1px solid #4f8ef7;'>
    <h1 style='color:#ffffff; margin:0; font-size:32px;'>
        🎓 EduPro Learner Analytics Dashboard
    </h1>
    <p style='color:#a0aec0; margin:6px 0 0 0; font-size:15px;'>
        Understanding learner demographics, course preferences & enrollment behavior
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    # Ensure the file name matches your actual file
    xls = pd.ExcelFile("project dashboard.xlsx")
    
    users        = pd.read_excel(xls, "users").drop_duplicates(subset="UserID")
    courses      = pd.read_excel(xls, "courses").drop_duplicates(subset="CourseID")
    transactions = pd.read_excel(xls, "transations").drop_duplicates()
    teachers     = pd.read_excel(xls, "Teachers").drop_duplicates(subset="TeacherID")

    # Parse dates
    transactions["TransactionDate"] = pd.to_datetime(transactions["TransactionDate"])
    transactions["Year"]  = transactions["TransactionDate"].dt.year
    transactions["MonthName"] = transactions["TransactionDate"].dt.strftime("%b")
    transactions["YearMonth"] = transactions["TransactionDate"].dt.to_period("M").astype(str)

    # Merge everything into one master dataframe
    df = (transactions
          .merge(users,    on="UserID")
          .merge(courses,  on="CourseID")
          .merge(teachers, on="TeacherID"))
    
    # Clean column names (remove hidden spaces)
    df.columns = df.columns.str.strip()
    return df

with st.spinner("Loading data..."):
    df = load_data()

st.success("✅ Data Loaded Successfully")

# -----------------------------
# SIDEBAR FILTERS (Safe logic)
# -----------------------------
with st.sidebar:
    st.markdown("## 🔍 Filters")
    st.markdown("---")

    # Safety checks for each column to prevent KeyError
    age_opts = sorted(df["Age"].unique()) if "Age" in df.columns else []
    age_filter = st.multiselect("👤 Age", options=age_opts, default=age_opts)

    gen_opts = df["Gender"].unique() if "Gender" in df.columns else []
    gender_filter = st.multiselect("⚥ Gender", options=gen_opts, default=gen_opts)

    cat_opts = sorted(df["CourseCategory"].unique()) if "CourseCategory" in df.columns else []
    category_filter = st.multiselect("📚 Course Category", options=cat_opts, default=cat_opts)

    lvl_opts = df["CourseLevel"].unique() if "CourseLevel" in df.columns else []
    level_filter = st.multiselect("🎯 Course Level", options=lvl_opts, default=lvl_opts)

    yr_opts = sorted(df["Year"].unique()) if "Year" in df.columns else []
    year_filter = st.multiselect("📅 Year", options=yr_opts, default=yr_opts)

# -----------------------------
# APPLY FILTERS (Safe logic)
# -----------------------------
filtered_df = df.copy()

if "Age" in filtered_df.columns and age_filter:
    filtered_df = filtered_df[filtered_df["Age"].isin(age_filter)]

if "Gender" in filtered_df.columns and gender_filter:
    filtered_df = filtered_df[filtered_df["Gender"].isin(gender_filter)]

if "CourseCategory" in filtered_df.columns and category_filter:
    filtered_df = filtered_df[filtered_df["CourseCategory"].isin(category_filter)]

if "CourseLevel" in filtered_df.columns and level_filter:
    filtered_df = filtered_df[filtered_df["CourseLevel"].isin(level_filter)]

if "Year" in filtered_df.columns and year_filter:
    filtered_df = filtered_df[filtered_df["Year"].isin(year_filter)]

# -----------------------------
# DOWNLOAD BUTTON
# -----------------------------
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📥 Export Data")
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Data",
        data=csv,
        file_name="edupro_filtered_data.csv",
        mime="text/csv"
    )

# -----------------------------
# KPIs (Safe logic)
# -----------------------------
active_users = filtered_df["UserID"].nunique() if "UserID" in filtered_df.columns else 0
total_courses = filtered_df["CourseID"].nunique() if "CourseID" in filtered_df.columns else 0
avg_courses = 0
if active_users > 0:
    avg_courses = round(filtered_df.groupby("UserID")["CourseID"].nunique().mean(), 2)

def kpi_card(col, label, value, icon, color="#4f8ef7"):
    col.markdown(f"""
    <div class='kpi-card' style='border-left-color:{color};'>
        <div class='kpi-label'>{icon} {label}</div>
        <div class='kpi-value'>{value}</div>
    </div>
    """, unsafe_allow_html=True)

k1,k2,k3,k4,k5 = st.columns(5)
kpi_card(k1, "Platform Engagement", f"{len(filtered_df):,}", "📊", "#4f8ef7")
kpi_card(k2, "Active Users", f"{active_users:,}", "👥", "#48bb78")
kpi_card(k3, "Avg Enrollments/User", avg_courses, "📈", "#ed8936")
kpi_card(k4, "Total Learners", f"{active_users:,}", "🎓", "#9f7aea")
kpi_card(k5, "Available Courses", total_courses, "📚", "#f56565")

# -----------------------------
# CHARTS (Simplified Overview)
# -----------------------------
st.markdown("<div class='section-title'>📋 Overview</div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    if "Age" in filtered_df.columns:
        age_data = filtered_df.groupby("Age")["UserID"].nunique().reset_index(name="Users")
        fig1 = px.bar(age_data, x="Users", y="Age", orientation="h", title="Enrollments by Age", template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    if "Gender" in filtered_df.columns:
        gen_data = filtered_df.groupby("Gender")["UserID"].nunique().reset_index(name="Users")
        fig2 = px.pie(gen_data, names="Gender", values="Users", title="Gender Breakdown", hole=0.5, template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

with col3:
    if "YearMonth" in filtered_df.columns:
        trend_data = filtered_df.groupby("YearMonth")["UserID"].nunique().reset_index(name="Users")
        fig3 = px.line(trend_data, x="YearMonth", y="Users", title="Enrollment Trends", template="plotly_dark")
        st.plotly_chart(fig3, use_container_width=True)

# FOOTER
st.markdown("<br><div style='text-align:center; color:#4a5568;'>EduPro Dashboard | Built with Streamlit</div>", unsafe_allow_html=True)
