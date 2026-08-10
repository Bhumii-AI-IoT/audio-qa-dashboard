"""
model.py
========
Risk prediction for audio QA projects.

WHAT THIS PREDICTS
------------------
Whether a project will finish BELOW the 90% approval quality gate,
using only signals known EARLY - before the project completes.

WHY THE FEATURES CHANGED
------------------------
The first version used 'rejected count' as a feature and 'approval rate
below 90%' as the label. Those are the same thing:

    approval_rate = 1 - (rejected / files_reviewed)

So the model was handed the answer. That is target leakage, and it is
why it reported 100% accuracy. Neither more data nor a train/test split
would have fixed it - the leak was in the features themselves.

This version uses only leading indicators - things a QA lead genuinely
knows in week one:

    language                 which language the project is in
    data_type                conversational AI / voice command / etc
    planned_files            total volume committed to
    annotator_count          how many people on the project
    pct_native_speakers      share of annotators native in the language
    avg_audio_seconds        mean clip length
    guideline_age_days       how stale the annotation guidelines are
    early_rejection_rate     rejection rate on the FIRST 10% of files

The last one is the key signal. It is genuinely available early and it
does not encode the final outcome.

DATA
----
All data here is SYNTHETIC. It is generated to reflect patterns I observe
during real QA work across Hindi, Gujarati and English, but it contains
no client data of any kind. This is a personal learning project and is
not connected to my employer.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

QUALITY_GATE = 90.0
RANDOM_SEED = 42

LANGUAGE_PROFILES = {
    "English":  {"base_approval": 95.0, "spread": 2.5},
    "Hindi":    {"base_approval": 88.5, "spread": 3.5},
    "Gujarati": {"base_approval": 83.0, "spread": 4.0},
}

DATA_TYPES = ["Conversational AI", "Voice Command", "Call Centre", "Read Speech"]


def generate_synthetic_projects(n_projects: int = 300,
                                seed: int = RANDOM_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []

    for i in range(n_projects):
        language = rng.choice(list(LANGUAGE_PROFILES.keys()), p=[0.45, 0.35, 0.20])
        profile = LANGUAGE_PROFILES[language]

        data_type = rng.choice(DATA_TYPES)
        planned_files = int(rng.integers(150, 1200))
        annotator_count = int(rng.integers(3, 25))

        native_ceiling = {"English": 1.0, "Hindi": 0.9, "Gujarati": 0.6}[language]
        pct_native = round(float(rng.uniform(0.2, native_ceiling)), 2)

        avg_audio_seconds = round(float(rng.uniform(4.0, 45.0)), 1)
        guideline_age_days = int(rng.integers(5, 400))

        approval = profile["base_approval"]
        approval += (pct_native - 0.5) * 9.0
        approval -= (guideline_age_days / 400) * 4.0
        approval -= max(0, (avg_audio_seconds - 25)) * 0.10
        approval += rng.normal(0, profile["spread"])
        approval = float(np.clip(approval, 60.0, 99.5))

        true_rejection = (100.0 - approval) / 100.0
        early_rejection_rate = float(np.clip(
            true_rejection + rng.normal(0, 0.06), 0.0, 1.0
        ))

        rows.append({
            "Project_Code": f"PROJ-{language[:2].upper()}-{i:03d}",
            "Language": language,
            "Data_Type": data_type,
            "Planned_Files": planned_files,
            "Annotator_Count": annotator_count,
            "Pct_Native_Speakers": pct_native,
            "Avg_Audio_Seconds": avg_audio_seconds,
            "Guideline_Age_Days": guideline_age_days,
            "Early_Rejection_Rate": round(early_rejection_rate, 3),
            "Final_Approval_Rate": round(approval, 1),
        })

    df = pd.DataFrame(rows)
    df["Below_Gate"] = (df["Final_Approval_Rate"] < QUALITY_GATE).astype(int)
    return df


FEATURES = [
    "Language",
    "Data_Type",
    "Planned_Files",
    "Annotator_Count",
    "Pct_Native_Speakers",
    "Avg_Audio_Seconds",
    "Guideline_Age_Days",
    "Early_Rejection_Rate",
]

# Never include these as features - they are the label in disguise.
# Kept here as a written reminder of what caused the original bug.

LEAKY_COLUMNS = ["Final_Approval_Rate", "Below_Gate", "Rejected", "Approved"]


def _encode(df: pd.DataFrame) -> pd.DataFrame:
    return pd.get_dummies(df[FEATURES], columns=["Language", "Data_Type"])


def train_risk_model(df: pd.DataFrame, seed: int = RANDOM_SEED):
    X = _encode(df)
    y = df["Below_Gate"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=seed, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        min_samples_leaf=5,
        random_state=seed,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="accuracy")

    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred) * 100, 1),
        "precision": round(precision_score(y_test, y_pred, zero_division=0) * 100, 1),
        "recall": round(recall_score(y_test, y_pred, zero_division=0) * 100, 1),
        "f1": round(f1_score(y_test, y_pred, zero_division=0) * 100, 1),
        "cv_mean": round(cv_scores.mean() * 100, 1),
        "cv_std": round(cv_scores.std() * 100, 1),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "pct_below_gate": round(y.mean() * 100, 1),
    }

    importance = (
        pd.DataFrame({
            "Feature": X.columns,
            "Importance": model.feature_importances_,
        })
        .sort_values("Importance", ascending=False)
        .reset_index(drop=True)
    )

    return model, metrics, importance

if __name__ == "__main__":
    data = generate_synthetic_projects()
    _, m, imp = train_risk_model(data)

    print(f"Projects generated : {len(data)}")
    print(f"Below quality gate : {m['pct_below_gate']}%")
    print(f"Train / test split : {m['n_train']} / {m['n_test']}")
    print()
    print(f"Held-out accuracy  : {m['accuracy']}%")
    print(f"Precision / Recall : {m['precision']}% / {m['recall']}%")
    print(f"5-fold CV          : {m['cv_mean']}% (+/- {m['cv_std']}%)")
    print()
    print(imp.head(10).to_string(index=False))


# ─────────────────────────────────────────────
# DISPLAY HELPER
#
# get_dummies splits Language into three separate columns
# (Language_English, Language_Hindi, Language_Gujarati), so the
# raw importance table shows them as three unrelated bars.
#
# That is misleading to read. This folds them back into one
# "Language" row so the chart matches how I actually think
# about the feature.
# ─────────────────────────────────────────────

# Columns that were one-hot encoded, and the label to show instead.
_GROUPED = {"Language": "Language", "Data_Type": "Audio type"}

# Tidier names for the plain numeric columns.
_LABELS = {
    "Planned_Files": "Planned volume",
    "Annotator_Count": "Annotator count",
    "Pct_Native_Speakers": "Native speaker share",
    "Avg_Audio_Seconds": "Average clip length",
    "Guideline_Age_Days": "Guideline age",
    "Early_Rejection_Rate": "Early rejection rate",
}


def group_importance(importance: pd.DataFrame) -> pd.DataFrame:
    """
    Combine one-hot dummy columns back into their parent feature.

    Takes the raw importance table from train_risk_model and returns
    a version with readable feature names, summed where a feature was
    split across several dummy columns.
    """
    totals = {}

    for _, row in importance.iterrows():
        name = row["Feature"]

        # Does this column come from a one-hot group?
        parent = None
        for prefix, label in _GROUPED.items():
            if name.startswith(prefix + "_"):
                parent = label
                break

        # Use the group label if it is a dummy, otherwise the tidy name.
        key = parent if parent else _LABELS.get(name, name)
        totals[key] = totals.get(key, 0.0) + row["Importance"]

    return (
        pd.DataFrame({
            "Feature": list(totals.keys()),
            "Importance": list(totals.values()),
        })
        .sort_values("Importance", ascending=False)
        .reset_index(drop=True)
    )