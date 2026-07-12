"""
model.py
========
Author: Bhumii Shah
Role: AI Data Quality Specialist

This file builds a simple machine learning model that
predicts whether a project will pass or fail the 90%
approval rate quality gate.

It learns from patterns in past project data:
- Language
- Data type
- Volume of files
- Rejection rate so far

This mirrors what an experienced QA reviewer does
naturally - using past experience to spot which
projects are likely to be difficult.
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

def predict_project_risk(df_projects):
    """
    Takes the project data and predicts which projects
    are at risk of failing the 90% quality gate.

    Input:  df_projects - the project DataFrame from data_loader.py
    Output: the same DataFrame with two new columns added:
            - Prediction: Pass or Fail
            - Risk_Score: probability of failing (0 to 100%)
    """

    # ─────────────────────────────────────────────
    # STEP 1: CREATE THE TARGET COLUMN
    # This is what the model is trying to predict.
    # 1 = Pass (approval rate is 90% or above)
    # 0 = Fail (approval rate is below 90%)
    # ─────────────────────────────────────────────
    df = df_projects.copy()
    df["Target"] = (df["Approval_Rate_%"] >= 90).astype(int)

    # ─────────────────────────────────────────────
    # STEP 2: CONVERT WORDS TO NUMBERS
    # ML models only understand numbers.
    # LabelEncoder converts "Hindi" → 0, "Gujarati" → 1
    # "English" → 2 (alphabetical order, automatically)
    # ─────────────────────────────────────────────
    le_lang      = LabelEncoder()
    le_type      = LabelEncoder()

    df["Language_Code"]  = le_lang.fit_transform(df["Language"])
    df["DataType_Code"]  = le_type.fit_transform(df["Data_Type"])

    # ─────────────────────────────────────────────
    # STEP 3: DEFINE FEATURES AND TARGET
    # Features = what the model learns FROM
    # Target   = what the model is trying to predict
    # ─────────────────────────────────────────────
    features = [
        "Language_Code",    # which language
        "DataType_Code",    # conversational AI vs voice command
        "Files_Reviewed",   # how many files in the project
        "Rejected",         # how many have been rejected so far
    ]

    X = df[features]   # input data (features)
    y = df["Target"]   # output data (pass or fail)

    # ─────────────────────────────────────────────
    # STEP 4: TRAIN THE MODEL
    # We use RandomForest — it builds multiple decision
    # trees and combines their votes for a final answer.
    # random_state=42 just means results are consistent
    # every time we run it (not random each time)
    # ─────────────────────────────────────────────
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # ─────────────────────────────────────────────
    # STEP 5: MAKE PREDICTIONS
    # predict()       → Pass or Fail (1 or 0)
    # predict_proba() → probability of each outcome
    #                   we take column 1 = probability of Pass
    # ─────────────────────────────────────────────
    predictions      = model.predict(X)
    probabilities    = model.predict_proba(X)[:, 1]

    # ─────────────────────────────────────────────
    # STEP 6: ADD RESULTS BACK TO THE DATAFRAME
    # Convert numbers back to readable labels
    # ─────────────────────────────────────────────
    df["Prediction"] = ["Pass" if p == 1 else "Fail" for p in predictions]
    df["Pass_Probability_%"] = (probabilities * 100).round(1)

    # Return only the columns we need for the dashboard
    return df[["Project_Code", "Language", "Status",
               "Approval_Rate_%", "Prediction", "Pass_Probability_%"]]