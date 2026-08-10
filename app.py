"""
app.py
======
Author: Bhumii Shah
Role: AI Data Quality - Final QA Reviewer

This dashboard tracks the health of audio and conversational
AI data quality review projects across three languages:
Hindi, Gujarati, and English.

I built this to visualise the kind of QA metrics I work
with day to day - approval rates, rejection patterns,
and project risk flags.

To run: streamlit run app.py
"""

import streamlit as st
import plotly.express as px
import data_loader
import model

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
df_projects   = data_loader.get_project_data()
df_languages  = data_loader.get_language_summary()
df_rejections = data_loader.get_rejection_reasons()
df_risks      = data_loader.get_risk_flags()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Filters")

    # Language filter - pulls unique values from data automatically
    lang_options = ["All Languages"] + sorted(df_projects["Language"].unique().tolist())
    selected_lang = st.selectbox("Language", lang_options)

    # Status filter
    status_options = ["All"] + sorted(df_projects["Status"].unique().tolist())
    selected_status = st.selectbox("Project Status", status_options)

    st.markdown("---")
    st.markdown("**Audio QA Project Dashboard**")
    st.markdown("Built by Bhumii Shah - AI Data Quality Specialist")

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
# AUTO SUMMARY INSIGHT
# Reads the data and surfaces the most important
# finding automatically - no hardcoding needed.
# This is what separates a dashboard from a table.
# ─────────────────────────────────────────────

# Find the language with the lowest approval rate
worst_lang = df_languages.loc[df_languages["Approval_Rate_%"].idxmin()]
worst_name = worst_lang["Language"]
worst_rate = worst_lang["Approval_Rate_%"]

# Count open risk flags
open_count = len(df_risks[df_risks["Status"] == "Open"])

# Count projects still not delivered
pending = len(df_projects[df_projects["Status"] != "Delivered"])

# Build the message based on what the data actually shows
if worst_rate < 85:
    severity = "error"
    message = (
        f"**Attention needed:** {worst_name} approval rate is at {worst_rate}% "
        f"- below the 90% quality gate. "
        f"{open_count} risk flags open. "
        f"{pending} projects pending delivery."
    )
elif worst_rate < 90:
    severity = "warning"
    message = (
        f"**Review recommended:** {worst_name} approval rate is at {worst_rate}% "
        f"- approaching the 90% quality gate. "
        f"{open_count} risk flags open. "
        f"{pending} projects pending delivery."
    )
else:
    severity = "success"
    message = (
        f"**All languages meeting quality gate.** "
        f"{open_count} risk flags open. "
        f"{pending} projects pending delivery."
    )

# Display the right colour banner based on severity
if severity == "error":
    st.error(message)
elif severity == "warning":
    st.warning(message)
else:
    st.success(message)

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

col1.metric("Files Reviewed",        f"{total_files:,}")
col2.metric("Approved",              f"{total_approved:,}")
col3.metric("Overall Approval Rate", f"{overall_rate}%", delta="Target: 90%")
col4.metric("Open Risk Flags",       open_risks)

st.markdown("---")

# ─────────────────────────────────────────────
# SECTION 2: APPROVAL RATE BY LANGUAGE
# Shows which languages are meeting the quality
# threshold and which are not
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
        # Colour scale goes red to yellow to green
        color_continuous_scale=["#ff6b6b", "#ffd43b", "#69db7c"],
        range_color=[75, 100],
        title="Approval Rate per Language (all projects)",
        text="Approval_Rate_%",
    )
    # Dashed line at 90% - the quality gate
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
        "Gujarati is the toughest - linguistically complex and smallest dataset. "
        "Hindi is affected by regional accent variation. "
        "English is the most consistent."
    )

st.markdown("---")

# ─────────────────────────────────────────────
# SECTION 3: REJECTION REASONS
# Shows what is actually going wrong - the patterns
# a QA reviewer spots over time
# ─────────────────────────────────────────────
st.subheader("Why Files Get Rejected")

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
# SECTION 4: PROJECT TRACKER
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
st.dataframe(
    styled.format({"Approval_Rate_%": "{:.1f}", "Gate_%": "{:.1f}"}),
    hide_index=True,
    use_container_width=True,
)

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
        if row["Severity"] == "High":
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
# SECTION 6: RECOMMENDATIONS
# Based on patterns observed during final QA review.
# These are not generic suggestions — they come from
# doing this work every day across three languages.
# ─────────────────────────────────────────────
st.subheader("Recommendations")

st.markdown("""
These recommendations come directly from patterns observed
during final QA review across Hindi, Gujarati, and English
audio projects.
""")

col_rec1, col_rec2, col_rec3 = st.columns(3)

with col_rec1:
    st.markdown("#### Gujarati — Annotator Pool")

    # Same reasoning as the Hindi block - read the rate from the
    # dataframe rather than typing it in.
    guj_rate = df_languages.loc[
        df_languages["Language"] == "Gujarati", "Approval_Rate_%"
    ].values[0]

    st.markdown(f"""
    Gujarati has the lowest approval rate at {guj_rate}% and the
    smallest dataset. The core issue is not just volume — it is
    that annotators without native or fluent Gujarati are making
    judgement calls they are not equipped to make.

    **Recommendation:** Prioritise native Gujarati speakers for
    this language. Where audio is genuinely incomprehensible —
    not just accented but unclear — annotators should have a
    defined right to skip rather than guess. A gap in the dataset
    is recoverable. A wrong transcription is not.
    """)
    
with col_rec2:
    st.markdown("#### Hindi — Guideline Update")

    # Pull the rate from the same dataframe the summary table uses,
    # so this sentence can never drift out of step with the table
    # above it. Hardcoding it is how the 88.1 / 87.1 mismatch happened.
    hindi_rate = df_languages.loc[
        df_languages["Language"] == "Hindi", "Approval_Rate_%"
    ].values[0]

    st.markdown(f"""
    Hindi approval rates sit at {hindi_rate}% — below the 90%
    quality gate. The main driver is regional accent
    variation. Bhojpuri-inflected Hindi and Rajasthani
    accent variants are not covered in current guidelines,
    so annotators default to guessing.

    **Recommendation:** Update annotation guidelines to
    include audio examples of the most common regional
    accent variants. Annotators should be able to match
    what they hear to a known category — not make it up
    as they go.
    """)

with col_rec3:
    st.markdown("#### All Languages — Living Guidelines")
    st.markdown("""
    Across all three languages, a recurring pattern is
    annotators encountering audio types that the guidelines
    do not cover. The current approach treats guidelines
    as fixed documents written before the project starts.

    **Recommendation:** Guidelines should be treated as
    living documents that are updated as new audio patterns
    emerge. When annotators regularly flag a type of audio
    the guidelines do not address, that is a signal to
    update — not to guess.
    """)

# ─────────────────────────────────────────────
# SECTION 7: EARLY RISK PREDICTION
#
# Predicts whether a project will finish below the 90% gate,
# using only signals available in the first weeks - before
# the outcome is known.
# ─────────────────────────────────────────────
st.markdown("---")
st.subheader("Early Risk Prediction")

st.markdown(
    "This model predicts whether a project will finish **below the 90% "
    "approval quality gate**, using only signals available in the first "
    "weeks of a project - before the outcome is known."
)


# Train once per session. Without the cache Streamlit retrains the model
# on every click and the dashboard becomes slow.
@st.cache_data
def load_risk_model():
    training_data = model.generate_synthetic_projects(n_projects=300)
    fitted, metrics, importance = model.train_risk_model(training_data)
    return training_data, metrics, model.group_importance(importance)


training_data, metrics, importance = load_risk_model()

st.info(
    "**The data behind this model is synthetic.** It is generated to "
    "reflect patterns I observe reviewing Hindi, Gujarati and English "
    "audio, but it contains no client data and no real project records."
)

# ─────────────────────────────────────────────
# HONEST METRICS
# Measured on projects the model never trained on.
# ─────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)

m1.metric("5-fold CV accuracy", f"{metrics['cv_mean']}%")
m1.caption(f"± {metrics['cv_std']}% - the stable number")

m2.metric("Held-out accuracy", f"{metrics['accuracy']}%")
m2.caption(f"On {metrics['n_test']} unseen projects")

m3.metric("Precision", f"{metrics['precision']}%")
m3.caption("When it flags, how often it is right")

m4.metric("Recall", f"{metrics['recall']}%")
m4.caption("Share of at-risk projects it catches")

st.caption(
    f"Trained on {metrics['n_train']} projects, scored on "
    f"{metrics['n_test']} it never saw. {metrics['pct_below_gate']}% of "
    "projects fall below the gate, so the classes are roughly balanced "
    "and accuracy is a meaningful measure rather than an inflated one."
)

with st.expander("How reliable is this, and where does it fall short?"):
    st.markdown(f"""
**Which number to trust**

I lead with the cross-validation score rather than the held-out score.
Held-out accuracy is measured on one particular split of
{metrics['n_test']} projects, and when I reran the whole thing across
seven different random seeds it moved between 80% and 91%. Cross-validation
re-splits the training data five ways and averages, so it moves far less.
{metrics['cv_mean']}% is the figure I would defend.

**What the trade-off means**

Precision of {metrics['precision']}% means that when the model flags a
project, it is nearly always right. Recall of {metrics['recall']}% means
it still misses some genuinely at-risk projects. For QA triage I would
rather it erred the other way - a false alarm costs one extra check,
a missed flag costs a late rework.

**What it does not do**

The training data is synthetic. The model demonstrates an approach; it
has not been validated against production outcomes.

**A note on the earlier version**

The first version of this section reported 100% accuracy and I was pleased
with it. It was wrong on two counts. It was scored on its own training
data, and one of its features - rejected count - was arithmetically the
same as the label, since approval rate is just one minus rejections over
files reviewed. I had handed the model the answer and asked it to work out
the answer. That is called target leakage, and neither more data nor a
train/test split would have fixed it. The fix was to change the question:
from *"given the finished numbers, did it fail?"* to *"given the setup and
the first batch, will it fail?"*
    """)

st.markdown("---")

# ─────────────────────────────────────────────
# FEATURE IMPORTANCE
# ─────────────────────────────────────────────
st.markdown("#### What drives the prediction")

col_fi1, col_fi2 = st.columns([3, 2])

with col_fi1:
    fig_imp = px.bar(
        importance.sort_values("Importance"),
        x="Importance",
        y="Feature",
        orientation="h",
        color="Importance",
        color_continuous_scale=["#a5d8ff", "#5c7cfa"],
        title="Feature importance - Random Forest",
        text="Importance",
    )
    fig_imp.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig_imp.update_layout(coloraxis_showscale=False, margin=dict(r=70))
    st.plotly_chart(fig_imp, use_container_width=True)

with col_fi2:
    # Pulled from the data rather than typed in, so this text cannot
    # drift out of step with the chart next to it.
    top = importance.iloc[0]
    native = importance.loc[importance["Feature"] == "Native speaker share",
                            "Importance"].values[0]
    headcount = importance.loc[importance["Feature"] == "Annotator count",
                               "Importance"].values[0]

    st.markdown(f"""
**{top['Feature']}** is the strongest signal at {top['Importance']:.2f}.
That matches what the approval rates show directly - English, Hindi and
Gujarati sit at consistently different levels, so knowing the language
already tells you a lot.

**Early rejection rate** is the most useful non-obvious signal. Rejection
patterns in the first tenth of a project tend to persist, which means
problems are visible well before delivery.

**Native speaker share** carries {native / headcount:.0f}x the weight of
raw annotator count ({native:.3f} against {headcount:.3f}). That is the
part I find most useful, because it supports the Gujarati recommendation
I had already written from experience: it is a staffing quality problem
before it is a headcount problem.
    """)
    
# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.caption(
    "Audio QA Project Dashboard · Built with Python & Streamlit · "
    "AI Data Quality Portfolio · github.com/Bhumii-AI-IoT"
)