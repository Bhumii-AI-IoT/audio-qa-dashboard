"""
app.py
======
Author: Bhumii Shah
Role: AI Data Quality Specialist — Final QA Reviewer

This dashboard tracks the health of audio and conversational
AI data quality review projects across three languages:
Hindi, Gujarati, and English.

I built this to visualise the kind of QA metrics I work
with day to day — approval rates, rejection patterns,
and project risk flags.

To run: streamlit run app.py
"""

import streamlit as st
import plotly.express as px
import data_loader

# ─────────────────────────────────────────────
# PAGE CONFIG
# Must be the very first Streamlit command
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Audio QA Project Dashboard",
    page_icon=None,
    layout="wide"
)

# ─────────────────────────────────────────────
# LOAD DATA
# Calling each function from data_loader.py
# ─────────────────────────────────────────────
df_projects  = data_loader.get_project_data()
df_languages = data_loader.get_language_summary()
df_rejections = data_loader.get_rejection_reasons()
df_risks     = data_loader.get_risk_flags()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛 Filters")

    # Language filter — pulls unique values from data automatically
    lang_options = ["All Languages"] + sorted(df_projects["Language"].unique().tolist())
    selected_lang = st.selectbox("Language", lang_options)

    # Status filter
    status_options = ["All"] + sorted(df_projects["Status"].unique().tolist())
    selected_status = st.selectbox("Project Status", status_options)

    st.markdown("---")
    st.markdown("**Audio QA Project Dashboard**")
    st.markdown("Built by Bhumii Shah · AI Data Quality Specialist")

# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
filtered = df_projects.copy()

if selected_lang != "All Languages":
    filtered = filtered[filtered["Language"] == selected_lang]

if selected_status != "All":
    filtered = filtered[filtered["Status"] == selected_status]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("Audio QA Project Dashboard")
st.caption(
    "Tracking approval rates, rejection patterns, and project risk "
    "across Hindi, Gujarati, and English audio QA projects."
)
st.markdown("---")

# ─────────────────────────────────────────────
# SECTION 1: KEY METRICS
# The four numbers a QA Lead checks first
# ─────────────────────────────────────────────
st.subheader("Overview")

total_files    = filtered["Files_Reviewed"].sum()
total_approved = filtered["Approved"].sum()
total_rejected = filtered["Rejected"].sum()
overall_rate   = round((total_approved / total_files) * 100, 1) if total_files > 0 else 0
open_risks     = len(df_risks[df_risks["Status"] == "Open"])

col1, col2, col3, col4 = st.columns(4)

col1.metric("Files Reviewed",   f"{total_files:,}")
col2.metric("Approved",         f"{total_approved:,}")
col3.metric("Overall Approval Rate", f"{overall_rate}%", delta="Target: 90%")
col4.metric("Open Risk Flags",  open_risks)

st.markdown("---")

# ─────────────────────────────────────────────
# SECTION 2: APPROVAL RATE BY LANGUAGE
# This is the core QA metric — shows which languages
# are meeting the quality threshold and which aren't
# ─────────────────────────────────────────────
st.subheader("Approval Rate by Language")

col_left, col_right = st.columns([3, 2])

with col_left:
    fig_lang = px.bar(
        df_languages.sort_values("Approval_Rate_%"),
        x="Approval_Rate_%",
        y="Language",
        orientation="h",
        color="Approval_Rate_%",
        # Colour scale goes red → yellow → green
        color_continuous_scale=["#ff6b6b", "#ffd43b", "#69db7c"],
        range_color=[75, 100],
        title="Approval Rate per Language (all projects)",
        text="Approval_Rate_%",
    )
    # Dashed line at 90% — the quality gate
    fig_lang.add_vline(
        x=90,
        line_dash="dash",
        line_color="white",
        annotation_text="90% quality gate",
        annotation_font_color="white"
    )
    fig_lang.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_lang.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_lang, use_container_width=True)

with col_right:
    st.markdown("#### Language Summary")
    st.dataframe(
        df_languages[["Language", "Approval_Rate_%", "Total_Files", "Top_Rejection_Reason"]],
        hide_index=True,
        use_container_width=True
    )
    st.caption(
        "Gujarati is the toughest — linguistically complex and smallest dataset. "
        "Hindi is affected by regional accent variation. "
        "English is the most consistent."
    )

st.markdown("---")

# ─────────────────────────────────────────────
# SECTION 3: REJECTION REASONS
# Shows what's actually going wrong — the patterns
# a QA reviewer spots over time
# ─────────────────────────────────────────────
st.subheader("Why Files Get Rejected?")

col_a, col_b = st.columns(2)

with col_a:
    fig_rej = px.bar(
        df_rejections.sort_values("Count"),
        x="Count",
        y="Rejection_Reason",
        orientation="h",
        color="Count",
        color_continuous_scale=["#ffd43b", "#ff6b6b"],
        title="Rejection Reason Breakdown",
        text="Count",
    )
    fig_rej.update_traces(textposition="outside")
    fig_rej.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_rej, use_container_width=True)

with col_b:
    st.markdown("#### Rejection Breakdown")
    st.dataframe(
        df_rejections,
        hide_index=True,
        use_container_width=True
    )
    st.caption(
        "Mispronunciation and accented speech transcription are the "
        "two most common failure points across all three languages."
    )

st.markdown("---")

# ─────────────────────────────────────────────
# SECTION 4: PROJECT TABLE
# Full view of all projects with approval rates
# ─────────────────────────────────────────────
st.subheader("Project Tracker")

# Colour code the Status column for quick scanning
def colour_status(val):
    if val == "Delivered":
        return "color: #69db7c"
    elif val == "In Final Review":
        return "color: #ffd43b"
    elif val == "In Progress":
        return "color: #4dabf7"
    else:
        return ""

styled = filtered.style.map(colour_status, subset=["Status"])
st.dataframe(styled, hide_index=True, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# SECTION 5: RISK FLAGS
# Open blockers that need attention
# ─────────────────────────────────────────────
st.subheader("Risk & Flag Monitor")

open_flags     = df_risks[df_risks["Status"] == "Open"]
resolved_flags = df_risks[df_risks["Status"] == "Resolved"]

col_r1, col_r2 = st.columns([2, 1])

with col_r1:
    st.markdown("#### Open Flags")
    for _, row in open_flags.iterrows():
     if row["Severity"] == "High" :\
     severity_label = "[HIGH]"
    else:
        severity_label = "[MEDIUM]"
        st.markdown(f"{severity_label} **{row['Flag']}** · `{row['Project']}`")
        st.caption(row["Description"])
        st.markdown("---")

with col_r2:
    st.markdown("#### Resolved")
    for _, row in resolved_flags.iterrows():
        st.markdown(f"{row['Flag']}")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.caption(
    "Audio QA Project Dashboard · Built with Python & Streamlit · "
    "AI Data Quality Portfolio · github.com/Bhumii-AI-IoT"
)