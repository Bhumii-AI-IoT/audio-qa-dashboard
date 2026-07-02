# Audio QA Project Dashboard
A project health and quality tracking dashboard for multilingual audio and conversational AI data — built with Python and Streamlit.

## What This Is

I work as an AI Data Quality Specialist reviewing audio and conversational AI training data across three languages — Hindi, Gujarati, and English.

This dashboard gives me visibility of quality across projects. Instead of waiting for feedback on where things need improving, I wanted to track it myself. So I built this.

It shows approval rates by language, rejection patterns, delivery status across projects, and active risk flags — the kind of view a QA lead or project manager needs in one place.

## Why I Built This

My background is in Global Project Management (MSc, University of Essex) but my day to day work is in AI data quality. This dashboard is where those two things meet.

I taught myself Python and built this as part of my own learning — not for a course, not for work, but because I wanted to turn the patterns I notice in my QA work into something visible and useful.

Before this, I relied on feedback from my manager to know where quality needed attention. Now I can see it myself.

## My Background

I studied Electronics and Communications Engineering in India before completing an MSc in Global Project Management at the University of Essex, London.

That combination — engineering fundamentals, project management methodology, and hands-on AI data quality work — is what this dashboard reflects.

Audio data quality is not just about catching errors. It is about understanding the full pipeline from signal to model output. My ECE background gives me a technical foundation for understanding audio data at a deeper level than a typical QA reviewer.

## What It Shows

- **Approval Rate by Language** — which languages are meeting the 90% quality gate and which are not
- **Rejection Reason Breakdown** — the most common errors caught during final QA review
- **Project Tracker** — delivery status across all active projects
- **Risk Flag Monitor** — open blockers with severity levels and descriptions

## Key Findings

These are not things I read somewhere — they come from doing the reviews myself every day:

- **Gujarati** is the hardest language to QA — linguistically complex and the smallest dataset
- **Hindi** suffers from regional accent variation that annotation guidelines do not fully account for
- **English** is the most consistent but accent misclassification still appears regularly

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly

## How to Run It

```bash
pip install -r requirements.txt
streamlit run app.py
```

## About Me

AI Data Quality Specialist based in London, working on 
multilingual audio and conversational AI training data.

BSc Electronics and Communications Engineering
MSc Global Project Management, University of Essex

I sit at the intersection of engineering, project management, 
and AI data quality. I am teaching myself Python and building 
tools that connect my day to day QA work with the kind of 
visibility a project manager needs.

This dashboard is one of those tools.