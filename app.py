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
    users = pd.read_excel(xls, "users").drop_duplicates(subset="UserID")
    courses = pd.read_excel(xls, "courses").drop_duplicates(subset="CourseID")
    transactions = pd.read_excel(xls, "transations").drop_duplicates()
    df = transactions.merge(users, on="UserID").merge(courses, on="CourseID")
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
        "👤 Age",
        options=sorted(df["Age"].unique()),
        default=sorted(df["Age"].unique())
    )

    gender_filter = st.multiselect(
        "⚥ Gender",
        options=df["Gender"].unique(),
        default=df["Gender"].unique()
    )

    category_filter = st.multiselect(
        "📚 Course Category",
        options=sorted(df["CourseCategory"].unique()),
        default=sorted(df["CourseCategory"].unique())
    )

    level_filter = st.multiselect(
        "🎯 Course Level",
        options=df["CourseLevel"].unique(),
        default=df["CourseLevel"].unique()
    )

    st.markdown("---")
    st.markdown("### 📥 Export Data")

filtered_df = df[
    (df["Age"].isin(age_filter)) &
    (df["Gender"].isin(gender_filter)) &
    (df["CourseCategory"].isin(category_filter)) &
    (df["CourseLevel"].isin(level_filter))
]

# Download button
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
total_enrollments = filtered_df["UserID"].nunique()
active_users = filtered_df["UserID"].nunique()
total_courses = filtered_df["CourseID"].nunique()
avg_courses = round(filtered_df.groupby("UserID")["CourseID"].nunique().mean(), 2)
coverage = round((active_users / df["UserID"].nunique()) * 100, 1)

k1, k2, k3, k4, k5 = st.columns(5)

def kpi_card(col, label, value, icon, color="#4f8ef7"):
    col.markdown(f"""
    <div class='kpi-card' style='border-left-color:{color};'>
        <div class='kpi-label'>{icon} {label}</div>
        <div class='kpi-value'>{value}</div>
    </div>
    """, unsafe_allow_html=True)

kpi_card(k1, "Total Enrollments", f"{total_enrollments:,}", "📋", "#4f8ef7")
kpi_card(k2, "Active Users",      f"{active_users:,}",      "👥", "#48bb78")
kpi_card(k3, "Avg Courses/User",  avg_courses,               "📈", "#ed8936")
kpi_card(k4, "Total Courses",     total_courses,             "🎓", "#9f7aea")
kpi_card(k5, "Filter Coverage",   f"{coverage}%",            "🎯", "#f56565")

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------
# ROW 1 — DEMOGRAPHICS
# -----------------------------
st.markdown("<div class='section-title'>👤 Learner Demographics</div>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    age_data = (
        filtered_df.groupby("Age")["UserID"]
        .nunique().reset_index(name="Users")
        .sort_values("Users", ascending=False)
    )
    fig1 = px.bar(age_data, x="Age", y="Users",
                  color="Users", color_continuous_scale="Blues",
                  title="👥 Learner Distribution by Age",
                  text="Users", template="plotly_dark")
    fig1.update_traces(textposition="outside")
    fig1.update_layout(showlegend=False, title_font_size=16)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    gender_data = (
        filtered_df.groupby("Gender")["UserID"]
        .nunique().reset_index(name="Users")
    )
    fig2 = px.pie(gender_data, names="Gender", values="Users",
                  title="⚥ Gender Participation Distribution",
                  hole=0.55, template="plotly_dark",
                  color_discrete_sequence=["#4f8ef7", "#48bb78", "#ed8936"])
    fig2.update_traces(textinfo="percent+label", pull=[0.03]*len(gender_data))
    fig2.update_layout(title_font_size=16)
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# ROW 2 — COURSE ANALYTICS
# -----------------------------
st.markdown("<div class='section-title'>📚 Course Analytics</div>", unsafe_allow_html=True)
col3, col4 = st.columns(2)

with col3:
    cat_data = (
        filtered_df.groupby("CourseCategory")["UserID"]
        .nunique().reset_index(name="Enrollments")
        .sort_values("Enrollments", ascending=True)
    )
    fig3 = px.bar(cat_data, x="Enrollments", y="CourseCategory",
                  orientation="h", color="Enrollments",
                  color_continuous_scale="Blues",
                  title="📊 Course Category Popularity",
                  text="Enrollments", template="plotly_dark")
    fig3.update_traces(textposition="outside")
    fig3.update_layout(showlegend=False, title_font_size=16,
                       yaxis_title="", xaxis_title="Enrollments")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    level_data = (
        filtered_df.groupby("CourseLevel")["UserID"]
        .nunique().reset_index(name="Enrollments")
    )
    fig4 = px.funnel(level_data, x="Enrollments", y="CourseLevel",
                     title="🎯 Course Level Preference",
                     template="plotly_dark",
                     color_discrete_sequence=["#4f8ef7"])
    fig4.update_layout(title_font_size=16)
    st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# ROW 3 — HEATMAP
# -----------------------------
st.markdown("<div class='section-title'>🔥 Enrollment Heatmap</div>", unsafe_allow_html=True)

heatmap_data = (
    filtered_df.groupby(["Age", "CourseCategory"])["UserID"]
    .nunique().reset_index(name="Users")
)
heatmap_pivot = heatmap_data.pivot(
    index="Age", columns="CourseCategory", values="Users"
).fillna(0)

fig5 = px.imshow(
    heatmap_pivot,
    title="🔥 Age vs Course Category Heatmap",
    color_continuous_scale="Blues",
    template="plotly_dark",
    text_auto=True,
    aspect="auto"
)
fig5.update_layout(title_font_size=16)
st.plotly_chart(fig5, use_container_width=True)

# -----------------------------
# KEY INSIGHTS
# -----------------------------
st.markdown("<div class='section-title'>📌 Key Insights</div>", unsafe_allow_html=True)

top_age      = age_data.sort_values("Users", ascending=False).iloc[0]["Age"]
top_age_cnt  = age_data.sort_values("Users", ascending=False).iloc[0]["Users"]
top_cat      = cat_data.sort_values("Enrollments", ascending=False).iloc[0]["CourseCategory"]
top_cat_cnt  = cat_data.sort_values("Enrollments", ascending=False).iloc[0]["Enrollments"]
top_level    = level_data.sort_values("Enrollments", ascending=False).iloc[0]["CourseLevel"]
top_gender   = gender_data.sort_values("Users", ascending=False).iloc[0]["Gender"]

insights = [
    f"🏆 Most active age group is <b>{top_age}</b> with <b>{top_age_cnt:,}</b> learners",
    f"📚 Most popular course category is <b>{top_cat}</b> with <b>{top_cat_cnt:,}</b> enrollments",
    f"🎯 Most preferred course level is <b>{top_level}</b>",
    f"👥 Dominant gender group is <b>{top_gender}</b>",
    f"📊 Average courses per user: <b>{avg_courses}</b>",
]

i1, i2 = st.columns(2)
for i, insight in enumerate(insights):
    col = i1 if i % 2 == 0 else i2
    col.markdown(f"<div class='insight-card'>{insight}</div>", unsafe_allow_html=True)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; color:#4a5568; font-size:13px; padding:20px;
     border-top: 1px solid #2d3748;'>
    🎓 EduPro Learner Analytics Dashboard | Built with Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
