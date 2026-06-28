"""
data_loader.py
==============
Author: Bhumii Shah
Role: AI Data Quality Specialist - Final QA Reviewer

This file holds all the data for the dashboard.
It reflects real working patterns from audio and
conversational AI data quality review projects.

Project codes follow a simple convention:
    PROJ-HI = Hindi projects
    PROJ-GU = Gujarati projects
    PROJ-EN = English projects

Quality gate: any project below 90% approval rate
cannot be marked as Delivered. It goes back into
Final Review until the issues are resolved.
"""

import pandas as pd


def get_project_data():
    """
    Returns a table of QA projects.

    Each row is one project batch that has gone through
    the full review pipeline:
    1. AI labelling
    2. Human annotation
    3. Final QA review (my role - I am the last human checkpoint)
    4. Client delivery - only happens when approval rate hits 90%+

    Note: PROJ-HI-002 was initially marked delivered at 87.1%
    but was flagged and returned to Final Review.
    This is a realistic scenario in multilingual audio QA.
    """
    data = {
        "Project_Code": [
            "PROJ-HI-001",
            "PROJ-HI-002",
            "PROJ-HI-003",
            "PROJ-GU-001",
            "PROJ-GU-002",
            "PROJ-EN-001",
            "PROJ-EN-002",
            "PROJ-EN-003",
        ],
        "Language": [
            "Hindi", "Hindi", "Hindi",
            "Gujarati", "Gujarati",
            "English", "English", "English",
        ],
        "Data_Type": [
            "Audio - Conversational AI",
            "Audio - Conversational AI",
            "Audio - Voice Command",
            "Audio - Conversational AI",
            "Audio - Voice Command",
            "Audio - Conversational AI",
            "Audio - Conversational AI",
            "Audio - Voice Command",
        ],
        # Status reflects realistic QA pipeline logic:
        # Nothing below 90% approval gets marked Delivered
        "Status": [
            "Delivered",        # 88.6% - borderline, approved after guideline review
            "In Final Review",  # 87.1% - flagged, returned for rework
            "In Final Review",  # 85.2% - still in review
            "Delivered",        # 83.2% - Gujarati threshold adjusted to 85% given complexity
            "In Final Review",  # 80.0% - needs more work
            "Delivered",        # 95.7% - well above threshold
            "Delivered",        # 95.8% - well above threshold
            "In Progress",      # 93.6% - still being reviewed
        ],
        "Files_Reviewed": [
            420, 380, 210,
            190, 140,
            510, 480, 220,
        ],
        "Approved": [
            372, 331, 179,
            158, 112,
            488, 460, 206,
        ],
        "Rejected": [
            48, 49, 31,
            32, 28,
            22, 20, 14,
        ],
    }

    df = pd.DataFrame(data)

    # Approval rate = files that passed final review / total files reviewed
    # This is the single most important metric in a QA pipeline
    df["Approval_Rate_%"] = round(
        (df["Approved"] / df["Files_Reviewed"]) * 100, 1
    )

    return df


def get_language_summary():
    """
    Returns approval rates rolled up by language.

    Patterns reflect real experience reviewing audio data:
    - English: highest approval rate - accent issues exist
      but the language stays intelligible across variants
    - Hindi: affected by regional accent variation (Bhojpuri,
      Rajasthani etc.) which creates genuine labelling ambiguity
    - Gujarati: toughest - linguistically complex and smallest
      dataset, so errors are harder to spot consistently
    """
    data = {
        "Language":        ["English", "Hindi",  "Gujarati"],
        "Total_Files":     [1210,      1010,     330],
        "Approval_Rate_%": [95.2,      87.1,     82.7],
        "Top_Rejection_Reason": [
            "Accent misclassification",
            "Regional accent ambiguity in intent labelling",
            "Linguistic complexity - morphology errors",
        ],
    }
    return pd.DataFrame(data)


def get_rejection_reasons():
    """
    Returns the most common reasons files get rejected
    during final QA review.

    These four error types come up repeatedly across
    audio and conversational AI projects:
    - Mispronunciation missed by the annotator
    - Wrong transcription because of a strong accent
    - Wrong intent label assigned to an utterance
    - Punctuation or grammar errors in the transcript
    """
    data = {
        "Rejection_Reason": [
            "Mispronunciation not flagged",
            "Wrong transcription - accented speech",
            "Incorrect intent labelling",
            "Punctuation / grammar error",
        ],
        "Count": [187, 143, 98, 76],
        "Most_Common_In": [
            "Hindi",
            "Gujarati",
            "Hindi",
            "English",
        ],
    }
    return pd.DataFrame(data)


def get_risk_flags():
    """
    Returns active risks and blockers across projects.

    Severity levels:
    - HIGH: blocking delivery, needs immediate action
    - MEDIUM: needs a plan, not urgent but cannot be ignored
    - LOW: minor issue, monitor and revisit

    These reflect real challenges in multilingual audio QA.
    """
    data = {
        "Project": [
            "PROJ-GU-002",
            "PROJ-HI-002",
            "PROJ-HI-003",
            "PROJ-EN-003",
        ],
        "Flag": [
            "Gujarati approval rate at 80% - well below quality gate",
            "Hindi intent labelling inconsistency blocking delivery",
            "Hindi accent variety not covered in current guidelines",
            "Guideline ambiguity - overlapping accent categories",
        ],
        "Severity": ["High", "High", "Medium", "Resolved"],
        "Status":   ["Open", "Open", "Open",   "Resolved"],
        "Description": [
            "PROJ-GU-002 at 80% approval - lowest across all projects. "
            "Gujarati is linguistically complex and the dataset is small. "
            "Flagged for guideline review and annotator re-calibration.",

            "PROJ-HI-002 returned to Final Review after delivery was attempted "
            "at 87.1% approval. Root cause: annotators inconsistently labelling "
            "overlapping intents in conversational AI data. Rework in progress.",

            "Current guidelines do not account for Bhojpuri-inflected Hindi "
            "or Rajasthani accent variants. Causing inconsistent labels "
            "across PROJ-HI-003. Guideline update raised with QA lead.",

            "English projects had ambiguous guidance on Indian English vs "
            "received pronunciation accent classification. "
            "Guidelines updated in v1.3 - issue now resolved.",
        ],
    }
    return pd.DataFrame(data)