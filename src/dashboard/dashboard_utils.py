import json
import pandas as pd
import sys
from pathlib import Path
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"

sys.path.append(str(SRC_DIR))
from load_candidates import load_candidates
from recruiter_explainer import generate_explanation
from scoring import get_score_breakdown
from career_intelligence import score_career_fit
from retrieval_intelligence import score_retrieval_intelligence


SUBMISSION_PATH = "outputs/final_submission.csv"


@st.cache_data
def load_submission():
    return pd.read_csv(SUBMISSION_PATH)


@st.cache_resource
def load_candidate_map():
    with open("outputs/dashboard_candidates.json", "r", encoding="utf-8") as f:
        return json.load(f)

    candidates = load_candidates()
    candidate_map = {}

    for candidate in candidates:
        candidate_id = candidate["candidate_id"]

        if candidate_id in required_ids:
            candidate_map[candidate_id] = candidate

        if len(candidate_map) == len(required_ids):
            break

    return candidate_map


def get_candidate(candidate_id, candidate_map):
    return candidate_map.get(candidate_id)


def get_candidate_explanation(candidate, final_score):
    breakdown = get_score_breakdown(candidate)
    breakdown["career_fit_score"] = score_career_fit(candidate)
    breakdown["retrieval_intelligence_score"] = score_retrieval_intelligence(candidate)

    return generate_explanation(candidate, breakdown, final_score)


def get_top_skills(candidate, limit=8):
    skills = candidate.get("skills", [])

    sorted_skills = sorted(
        skills,
        key=lambda s: (
            s.get("proficiency", "") in ["expert", "advanced"],
            s.get("endorsements", 0),
            s.get("duration_months", 0),
        ),
        reverse=True,
    )

    return [skill.get("name", "") for skill in sorted_skills[:limit] if skill.get("name")]


def get_dashboard_metrics(df):
    return {
        "top_score": round(df["score"].max(), 2),
        "avg_score": round(df["score"].mean(), 2),
        "total_ranked": len(df),
        "lowest_score": round(df["score"].min(), 2),
    }