import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="EduPro Dashboard", layout="wide")

st.title("📊 EduPro Learner Analytics Dashboard")
st.markdown(
    "### understanding learner demograhics, course preferences, and enrollment behavior"
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():

    # READ EXCEL FILE
    xls = pd.ExcelFile("project dashboard.xlsx")

    # SHEETS
    users = pd.read_excel(xls, "users")
    courses = pd.read_excel(xls, "courses")
    transactions = pd.read_excel(xls, "transations")

    # REMOVE DUPLICATES
    users = users.drop_duplicates(subset="UserID")
    courses = courses.drop_duplicates(subset="CourseID")
    transactions = transactions.drop_duplicates()

    # MERGE TABLES
    df = transactions.merge(users, on="UserID")
    df = df.merge(courses, on="CourseID")

    return df

df = load_data()

st.success("Data Loaded Successfully ✅")

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")

age_filter = st.sidebar.multiselect(
    "Select Age",
    options=df["Age"].unique(),
    default=df["Age"].unique()
)

gender_filter = st.sidebar.multiselect(
    "Select Gender",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

filtered_df = df[
    (df["Age"].isin(age_filter)) &
    (df["Gender"].isin(gender_filter))
]

# -----------------------------
# KPIs (USER_ID BASED)
# -----------------------------
total_users = filtered_df["UserID"].nunique()

total_enrollments = filtered_df["UserID"].nunique()

active_users = filtered_df["UserID"].nunique()

total_courses = filtered_df["CourseID"].nunique()

avg_courses = round(
    filtered_df.groupby("UserID")["CourseID"].nunique().mean(),
    2
)

# -----------------------------
# KPI ROW
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Enrollments", total_enrollments)
c2.metric("Active Users", active_users)
c3.metric("Avg Courses/User", avg_courses)
c4.metric("Total Courses", total_courses)

# -----------------------------
# AGE GROUP ANALYSIS
# DISTINCT USERS ONLY
# -----------------------------
age_data = (
    filtered_df.groupby("Age")["UserID"]
    .nunique()
    .reset_index(name="Enrollments")
)

age_chart = px.bar(
    age_data,
    x="Age",
    y="Enrollments",
    color="Enrollments",
    title="learner distribution by age group",
    text="Enrollments"
)

# -----------------------------
# GENDER ANALYSIS
# -----------------------------
gender_data = (
    filtered_df.groupby("Gender")["UserID"]
    .nunique()
    .reset_index(name="Users")
)

gender_chart = px.pie(
    gender_data,
    names="Gender",
    values="Users",
    title="Gender Participation distribution",
    hole=0.5
)

# -----------------------------
# CATEGORY ANALYSIS
# -----------------------------
category_data = (
    filtered_df.groupby("CourseCategory")["UserID"]
    .nunique()
    .reset_index(name="Enrollments")
)

category_chart = px.bar(
    category_data,
    x="CourseCategory",
    y="Enrollments",
    color="Enrollments",
    title="Course Category Popularity",
    text="Enrollments"
)

# -----------------------------
# COURSE LEVEL ANALYSIS
# -----------------------------
level_data = (
    filtered_df.groupby("CourseLevel")["UserID"]
    .nunique()
    .reset_index(name="Enrollments")
)

level_chart = px.bar(
    level_data,
    x="CourseLevel",
    y="Enrollments",
    color="Enrollments",
    title="Course Level Preference Distribution",
    text="Enrollments"
)

# -----------------------------
# CHART LAYOUT
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(age_chart, use_container_width=True)

with col2:
    st.plotly_chart(gender_chart, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.plotly_chart(category_chart, use_container_width=True)

with col4:
    st.plotly_chart(level_chart, use_container_width=True)

# -----------------------------
# INSIGHTS
# -----------------------------
top_age = age_data.sort_values(
    by="Enrollments",
    ascending=False
).iloc[0]["Age"]

top_category = category_data.sort_values(
    by="Enrollments",
    ascending=False
).iloc[0]["CourseCategory"]

top_level = level_data.sort_values(
    by="Enrollments",
    ascending=False
).iloc[0]["CourseLevel"]

st.subheader("📌 Key Insights")

st.write(f"✅ Most active age group: {top_age}")
st.write(f"✅ Most popular course category: {top_category}")
st.write(f"✅ Most preferred course level: {top_level}")
