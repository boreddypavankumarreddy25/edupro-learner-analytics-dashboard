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
    xls = pd.ExcelFile("project dashboard.xlsx")
    users        = pd.read_excel(xls, "users").drop_duplicates(subset="UserID")
    courses      = pd.read_excel(xls, "courses").drop_duplicates(subset="CourseID")
    transactions = pd.read_excel(xls, "transations").drop_duplicates()
    teachers     = pd.read_excel(xls, "Teachers").drop_duplicates(subset="TeacherID")

    # parse date
    transactions["TransactionDate"] = pd.to_datetime(transactions["TransactionDate"])
    transactions["Year"]  = transactions["TransactionDate"].dt.year
    transactions["Month"] = transactions["TransactionDate"].dt.month
    transactions["MonthName"] = transactions["TransactionDate"].dt.strftime("%b")
    transactions["YearMonth"] = transactions["TransactionDate"].dt.to_period("M").astype(str)

    df = (transactions
          .merge(users,    on="UserID")
          .merge(courses,  on="CourseID")
          .merge(teachers, on="TeacherID"))
    return df

with st.spinner("Loading data..."):
    df = load_data()

st.success("✅ Data Loaded Successfully")

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
with st.sidebar:
    st.markdown("## 🔍 Filters")
    st.markdown("---")

    age_filter = st.multiselect(
        "👤 Age", options=age_options,
        default=age_options
    )
    gender_filter = st.multiselect(
        "⚥ Gender", options=df["Gender"].unique(),
        default=df["Gender"].unique()
    )
    category_filter = st.multiselect(
        "📚 Course Category", options=sorted(df["CourseCategory"].unique()),
        default=sorted(df["CourseCategory"].unique())
    )
    level_filter = st.multiselect(
        "🎯 Course Level", options=df["CourseLevel"].unique(),
        default=df["CourseLevel"].unique()
    )
    year_filter = st.multiselect(
        "📅 Year", options=sorted(df["Year"].unique()),
        default=sorted(df["Year"].unique())
    )

    st.markdown("---")
    st.markdown("### 📥 Export Data")

filtered_df = df[
    (df["Age"].isin(age_filter)) &
    (df["Gender"].isin(gender_filter)) &
    (df["CourseCategory"].isin(category_filter)) &
    (df["CourseLevel"].isin(level_filter)) &
    (df["Year"].isin(year_filter))
]

with st.sidebar:
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Data",
        data=csv,
        file_name="edupro_filtered_data.csv",
        mime="text/csv"
    )

# -----------------------------
# KPIs
# -----------------------------
active_users      = filtered_df["UserID"].nunique()
total_enrollments = active_users
total_courses     = filtered_df["CourseID"].nunique()
avg_courses       = round(filtered_df.groupby("UserID")["CourseID"].nunique().mean(), 2)
coverage          = round((active_users / df["UserID"].nunique()) * 100, 1)
platform_engage   = active_users

def kpi_card(col, label, value, icon, color="#4f8ef7"):
    col.markdown(f"""
    <div class='kpi-card' style='border-left-color:{color};'>
        <div class='kpi-label'>{icon} {label}</div>
        <div class='kpi-value'>{value}</div>
    </div>
    """, unsafe_allow_html=True)

k1,k2,k3,k4,k5 = st.columns(5)
kpi_card(k1, "Platform Engagement", f"{platform_engage:,}", "📊", "#4f8ef7")
kpi_card(k2, "Active Users",        f"{active_users:,}",    "👥", "#48bb78")
kpi_card(k3, "Avg Enrollments/User",avg_courses,            "📈", "#ed8936")
kpi_card(k4, "Total Learners",      f"{active_users:,}",    "🎓", "#9f7aea")
kpi_card(k5, "Available Courses",   total_courses,          "📚", "#f56565")

st.markdown("<br>", unsafe_allow_html=True)

# =============================================
# PAGE 1 — OVERVIEW
# =============================================
st.markdown("<div class='section-title'>📋 Overview</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# Age group bar
with col1:
    age_data = (
        filtered_df.groupby("Age")["UserID"]
        .nunique().reset_index(name="ActiveUsers")
        .sort_values("ActiveUsers", ascending=True)
    )
    fig1 = px.bar(age_data, x="ActiveUsers", y="Age", orientation="h",
                  color="ActiveUsers", color_continuous_scale="Blues",
                  title="👥 Enrollments by Age Group", text="ActiveUsers",
                  template="plotly_dark")
    fig1.update_traces(textposition="outside")
    fig1.update_layout(showlegend=False, title_font_size=15, yaxis_title="Age Group")
    st.plotly_chart(fig1, use_container_width=True)

# Gender donut
with col2:
    gender_data = (
        filtered_df.groupby("Gender")["UserID"]
        .nunique().reset_index(name="Users")
    )
    fig2 = px.pie(gender_data, names="Gender", values="Users",
                  title="⚥ Gender Participation Ratio", hole=0.55,
                  template="plotly_dark",
                  color_discrete_sequence=["#4f8ef7","#48bb78"])
    fig2.update_traces(textinfo="percent+label", pull=[0.03]*len(gender_data))
    fig2.update_layout(title_font_size=15)
    st.plotly_chart(fig2, use_container_width=True)

# Enrollment trend over time
with col3:
    trend_data = (
        filtered_df.groupby("YearMonth")["UserID"]
        .nunique().reset_index(name="Enrollments")
        .sort_values("YearMonth")
    )
    fig3 = px.line(trend_data, x="YearMonth", y="Enrollments",
                   title="📅 Enrollment Trends Over Time",
                   markers=True, template="plotly_dark",
                   color_discrete_sequence=["#4f8ef7"])
    fig3.update_layout(title_font_size=15,
                       xaxis_title="Month", yaxis_title="Enrollments")
    st.plotly_chart(fig3, use_container_width=True)

# =============================================
# PAGE 2 — COURSE PREFERENCES
# =============================================
st.markdown("<div class='section-title'>📚 Course Preferences</div>", unsafe_allow_html=True)

col4, col5 = st.columns(2)

# Category by Age Group
with col4:
    cat_age = (
        filtered_df.groupby(["Age","CourseCategory"])["UserID"]
        .nunique().reset_index(name="Enrollments")
    )
    fig4 = px.bar(cat_age, x="Enrollments", y="Age", color="CourseCategory",
                  orientation="h", barmode="stack",
                  title="📊 Category Preference by Age Group",
                  template="plotly_dark")
    fig4.update_layout(title_font_size=15, yaxis_title="Age Group",
                       legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(fig4, use_container_width=True)

# Category by Gender
with col5:
    cat_gender = (
        filtered_df.groupby(["CourseCategory","Gender"])["UserID"]
        .nunique().reset_index(name="Enrollments")
    )
    fig5 = px.bar(cat_gender, x="Enrollments", y="CourseCategory",
                  color="Gender", orientation="h", barmode="group",
                  title="📊 Category by Gender",
                  template="plotly_dark",
                  color_discrete_sequence=["#4f8ef7","#48bb78"])
    fig5.update_layout(title_font_size=15, yaxis_title="")
    st.plotly_chart(fig5, use_container_width=True)

# Heatmap
st.markdown("<div class='section-title'>🔥 Heatmap — Age vs Course Category</div>", unsafe_allow_html=True)
heatmap_pivot = (
    filtered_df.groupby(["Age","CourseCategory"])["UserID"]
    .nunique().reset_index(name="Users")
    .pivot(index="Age", columns="CourseCategory", values="Users")
    .fillna(0)
)
fig6 = px.imshow(heatmap_pivot, title="🔥 Age vs Course Category",
                 color_continuous_scale="Blues", template="plotly_dark",
                 text_auto=True, aspect="auto")
fig6.update_layout(title_font_size=15)
st.plotly_chart(fig6, use_container_width=True)

# =============================================
# PAGE 3 — COURSE LEVEL INSIGHTS
# =============================================
st.markdown("<div class='section-title'>🎯 Course Level Insights</div>", unsafe_allow_html=True)

col6, col7, col8 = st.columns(3)

# Level by Age
with col6:
    lvl_age = (
        filtered_df.groupby(["Age","CourseLevel"])["UserID"]
        .nunique().reset_index(name="Enrollments")
    )
    fig7 = px.bar(lvl_age, x="Enrollments", y="Age", color="CourseLevel",
                  orientation="h", barmode="stack",
                  title="🎯 Level by Age Group",
                  template="plotly_dark")
    fig7.update_layout(title_font_size=15, yaxis_title="Age Group",
                       legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(fig7, use_container_width=True)

# Level by Gender
with col7:
    lvl_gender = (
        filtered_df.groupby(["Gender","CourseLevel"])["UserID"]
        .nunique().reset_index(name="Enrollments")
    )
    fig8 = px.bar(lvl_gender, x="Enrollments", y="Gender", color="CourseLevel",
                  orientation="h", barmode="stack",
                  title="🎯 Level by Gender",
                  template="plotly_dark")
    fig8.update_layout(title_font_size=15, yaxis_title="",
                       legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(fig8, use_container_width=True)

# Teacher Performance
with col8:
    teacher_data = (
        filtered_df.groupby("TeacherName")["UserID"]
        .nunique().reset_index(name="Enrollments")
        .sort_values("Enrollments", ascending=False)
        .head(10)
    )
    fig9 = px.bar(teacher_data, x="TeacherName", y="Enrollments",
                  color="Enrollments", color_continuous_scale="Blues",
                  title="👨‍🏫 Teacher Performance",
                  text="Enrollments", template="plotly_dark")
    fig9.update_traces(textposition="outside")
    fig9.update_layout(showlegend=False, title_font_size=15,
                       xaxis_tickangle=-30)
    st.plotly_chart(fig9, use_container_width=True)

# =============================================
# KEY INSIGHTS
# =============================================
st.markdown("<div class='section-title'>📌 Key Insights</div>", unsafe_allow_html=True)

age_data2   = filtered_df.groupby("Age")["UserID"].nunique().reset_index(name="U")
cat_data2   = filtered_df.groupby("CourseCategory")["UserID"].nunique().reset_index(name="U")
level_data2 = filtered_df.groupby("CourseLevel")["UserID"].nunique().reset_index(name="U")
top_teacher = teacher_data.iloc[0]["TeacherName"]
top_teacher_cnt = teacher_data.iloc[0]["Enrollments"]

insights = [
    f"🏆 Most active age group: <b>{age_data2.sort_values('U',ascending=False).iloc[0]['Age']}</b>",
    f"📚 Most popular category: <b>{cat_data2.sort_values('U',ascending=False).iloc[0]['CourseCategory']}</b>",
    f"🎯 Most preferred level: <b>{level_data2.sort_values('U',ascending=False).iloc[0]['CourseLevel']}</b>",
    f"👨‍🏫 Top teacher: <b>{top_teacher}</b> with <b>{top_teacher_cnt:,}</b> enrollments",
    f"👥 Male users dominate enrollments (~{round(gender_data[gender_data['Gender']=='Male']['Users'].values[0]/gender_data['Users'].sum()*100)}%)" if 'Male' in gender_data['Gender'].values else "👥 See gender chart for breakdown",
    f"📊 Average courses per user: <b>{avg_courses}</b>",
]

i1, i2 = st.columns(2)
for i, ins in enumerate(insights):
    (i1 if i%2==0 else i2).markdown(
        f"<div class='insight-card'>{ins}</div>", unsafe_allow_html=True
    )

# FOOTER
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; color:#4a5568; font-size:13px; padding:20px;
     border-top: 1px solid #2d3748;'>
    🎓 EduPro Learner Analytics Dashboard | Built with Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
