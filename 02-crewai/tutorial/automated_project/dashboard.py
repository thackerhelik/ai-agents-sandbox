import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

# Set up page configuration
st.set_page_config(
    page_title="Project Schedule & Resource Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. Dynamic Live Data Loader
@st.cache_data
def load_live_data():
    file_path="final_project_plan.json"

    # Fall back if the AI pipeline hasn't run yet
    if not os.path.exists(file_path):
        st.error(f"⚠️ '{file_path}' not found! Please run your backend AI pipeline first to generate the data.")
        st.stop()
        
    with open(file_path, "r") as f:
        return json.load(f)

# 1. Raw Dataset
DATA = load_live_data()

# 2. Data Processing Pipelines
@st.cache_data
def process_project_data():
    # Flatten tasks to create a core DataFrame
    tasks_df = pd.DataFrame(DATA["tasks"])

    # Map each task to its parent milestone
    task_to_milestone = {}
    for m in DATA["milestones"]:
        for t_id in m["tasks"]:
            task_to_milestone[t_id] = m["milestone_name"]

    tasks_df["milestone"] = tasks_df["task_id"].map(task_to_milestone)

    # Explore resource arrays to directly analyze workload variations
    exploded_resources = tasks_df.explode("required_resources")

    return tasks_df, exploded_resources

df_tasks, df_resources = process_project_data()

# 3. Sidebar Filtering Implementation
st.sidebar.title("🛠️ Project Controls")
st.sidebar.markdown("Filter view metrics across sprint phases.")

all_milestones = ["All Milestones"] + list(df_tasks["milestone"].unique())
selected_milestone = st.sidebar.selectbox("Select Phase/Milestone:", all_milestones)

all_resources = ["All Team Members"] + list(df_resources["required_resources"].dropna().unique())
selected_resource = st.sidebar.selectbox("Filter by Resource Allocation:", all_resources)

# All operational filtering logic
filtered_tasks = df_tasks.copy()
filtered_resources = df_resources.copy()

if selected_milestone != "All Milestones":
    filtered_tasks = filtered_tasks[filtered_tasks["milestone"] == selected_milestone]
    filtered_resources = filtered_resources[filtered_resources["milestone"] == selected_milestone]

if selected_resource != "All Team Members":
    # Filter tasks where the list contains the target resource string
    filtered_tasks = filtered_tasks[filtered_tasks["required_resources"].apply(lambda x: selected_resource in x)]
    filtered_resources = filtered_resources[filtered_resources["required_resources"] == selected_resource]

# 4. Global Title Structure
st.title("🚀 Enterprise Project Schedule Analytics Dashboard")
st.markdown(f"**Current Scope Visualization:** {selected_milestone} | **Resource Context:** {selected_resource}")
st.divider()

# 5. Core High-Level KPI Layout
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Scope Hours", value=f"{filtered_tasks['estimated_time_hours'].sum():.1f} hrs")
with col2:
    st.metric(label="Task Count", value=len(filtered_tasks))
with col3:
    st.metric(label="Active Milestones", value=filtered_tasks["milestone"].nunique())
with col4:
    st.metric(label="Assigned Devs/QA", value=df_resources[df_resources["task_id"].isin(filtered_tasks["task_id"])]["required_resources"].nunique())

st.markdown("---")

# 6. Primary Interactive Chart Viewports
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("⏳ Hour Distribution by Milestone Grouping")
    milestone_hours = filtered_tasks.groupby("milestone")["estimated_time_hours"].sum().reset_index()
    fig_milestone = px.bar(
        milestone_hours,
        x="estimated_time_hours",
        y="milestone",
        orientation="h",
        labels={"estimated_time_hours": "Total Hours", "milestone": "Milestone Phase"},
        text_auto=".1f",
        template="plotly_dark"
    )
    fig_milestone.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_milestone, width="stretch")

with chart_col2:
    st.subheader("👷 Resource Load Breakdown (Total Cumulative Hours)")
    resource_hours = filtered_resources.groupby("required_resources")["estimated_time_hours"].sum().reset_index()
    fig_resource = px.pie(
        resource_hours,
        values="estimated_time_hours",
        names="required_resources",
        hole=0.4,
        template="plotly_dark"
    )
    fig_resource.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_resource, width="stretch")

st.markdown("---")

# 7. Granular Task Data Matrix
st.subheader("📋 Scope Ledger View Matrix")
display_columns = ["task_id", "task_name", "estimated_time_hours", "required_resources", "milestone"]
st.dataframe(
    filtered_tasks[display_columns],
    column_config={
        "task_id": "ID",
        "task_name": "Task Description",
        "estimated_time_hours": st.column_config.NumberColumn("Hours", format="%.1f hrs"),
        "required_resources": "Assigned Resources",
        "milestone": "Project Milestone"
    },
    hide_index=True,
    width="stretch"
)