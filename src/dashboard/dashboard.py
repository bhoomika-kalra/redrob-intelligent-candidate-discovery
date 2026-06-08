import sys
from pathlib import Path

import streamlit as st
from PIL import Image

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"

sys.path.append(str(CURRENT_DIR))
sys.path.append(str(SRC_DIR))

from insights import build_recruiter_insights
from dashboard_utils import (
    load_submission,
    load_candidate_map,
    get_candidate,
    get_candidate_explanation,
    get_top_skills,
    get_dashboard_metrics,
)
from charts import score_distribution_chart, top_candidates_chart

def section_header(title):
    st.markdown(
        f"""
        <div style="
        border-left:6px solid #6D28D9;
        padding-left:14px;
        font-size:30px;
        font-weight:700;
        margin-top:10px;
        margin-bottom:20px;
        ">
        {title}
        </div>
        """,
        unsafe_allow_html=True,
    )

def get_score_badge(score):
    if score >= 75:
        return "Strong Fit"
    elif score >= 50:
        return "Good Fit"
    else:
        return "Review Carefully"


def render_fit_box(score):
    if score >= 75:
        st.success(f"Score: {round(score, 2)}")
    elif score >= 50:
        st.warning(f"Score: {round(score, 2)}")
    else:
        st.error(f"Score: {round(score, 2)}")


st.set_page_config(
    page_title="Redrob AI Recruiter",
    layout="wide",
)

st.sidebar.markdown("## DASHBOARD")

page = st.sidebar.segmented_control(
    "",
    [
        "Dashboard Overview",
        "Candidate Explorer",
    ],
    default="Dashboard Overview",
)

st.markdown(
    """
    <style>
    .main {
        background-color: #F7F9FC;
    }

    .hero-box {
        background: linear-gradient(135deg, #1E3A8A, #6D28D9);
        padding: 22px;
        border-radius: 18px;
        color: white;
        margin-bottom: 25px;
    }

    .hero-title {
        font-size: 26px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 18px;
        opacity: 0.9;
    }
    
    div[data-testid="stSegmentedControl"] {
        background-color: blue;
    }

    div[data-testid="stSegmentedControl"] button {
        border-radius: 12px;
        padding: 10px 14px;
        font-weight: 600;
    }
    
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
logo_path = ROOT_DIR / "assets" / "logo.png"

header_col1, header_col2 = st.columns([1, 8])

with header_col1:
    if logo_path.exists():
        logo = Image.open(logo_path)
        st.image(logo, width=120)

with header_col2:
    st.markdown(
        """
        <div class="hero-box">
            <div class="hero-title">
                Redrob AI Recruiter
            </div>
            <div class="hero-subtitle">
                AI-powered candidate discovery, ranking,
                explainability, and recruiter decision support.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# Load data
df = load_submission()
candidate_map = load_candidate_map()
metrics = get_dashboard_metrics(df)
insights = build_recruiter_insights(df)


# =========================
# PAGE 1: OVERVIEW DASHBOARD
# =========================
if page == "Dashboard Overview":

    section_header("Recruiter Overview")

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    metric_col1.metric("Top Score", metrics["top_score"])
    metric_col2.metric("Average Score", metrics["avg_score"])
    metric_col3.metric("Candidates Ranked", metrics["total_ranked"])
    metric_col4.metric("Lowest Score", metrics["lowest_score"])

    st.divider()

    section_header("Recruiter Insights")

    insight_col1, insight_col2, insight_col3, insight_col4 = st.columns(4)

    with insight_col1:
        st.metric("Strong Fit Candidates", insights["strong_fit_count"])

    with insight_col2:
        st.metric("Good Fit Candidates", insights["good_fit_count"])

    with insight_col3:
        st.metric("Low Priority", insights["review_count"])

    with insight_col4:
        st.metric("Top Candidate", insights["top_candidate"])

    st.divider()

    section_header("Top Talent Picks")

    top_3 = df.head(3)
    talent_col1, talent_col2, talent_col3 = st.columns(3)
    talent_cols = [talent_col1, talent_col2, talent_col3]

    for idx, (_, row) in enumerate(top_3.iterrows()):
        candidate = get_candidate(row["candidate_id"], candidate_map)
        profile = candidate.get("profile", {}) if candidate else {}

        title = profile.get("current_title", "Unknown")
        experience = profile.get("years_of_experience", "NA")
        score = round(float(row["score"]), 2)

        with talent_cols[idx]:
            with st.container(border=True):
                st.markdown(f"## Rank {int(row['rank'])}")
                st.markdown(f"### {row['candidate_id']}")
                st.write(f"**Role:** {title}")
                st.write(f"**Experience:** {experience} years")
                render_fit_box(score)
                st.write(get_score_badge(score))

    st.divider()

    section_header("Ranking Analytics")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.plotly_chart(top_candidates_chart(df), use_container_width=True)

    with chart_col2:
        st.plotly_chart(score_distribution_chart(df), use_container_width=True)


# =========================
# PAGE 2: CANDIDATE EXPLORER
# =========================
elif page == "Candidate Explorer":

    st.sidebar.title("Candidate Controls")

    top_n = st.sidebar.slider(
        "Leaderboard Count",
        min_value=10,
        max_value=100,
        value=25,
        step=5,
    )

    min_score = st.sidebar.slider(
        "Minimum Score",
        min_value=float(df["score"].min()),
        max_value=float(df["score"].max()),
        value=float(df["score"].min()),
    )

    role_filter = st.sidebar.text_input(
    "Role / Skill Filter",
    )
    candidate_search = st.sidebar.selectbox(
    "Candidate ID Lookup",
    ["Select Candidate"] + df["candidate_id"].tolist()
    )

    filtered_df = df[df["score"] >= min_score]

    if role_filter:
        filtered_df = filtered_df[
            filtered_df["reasoning"]
            .str.lower()
            .str.contains(role_filter.lower(), na=False)
        ]

    if candidate_search != "Select Candidate":
        filtered_df = filtered_df[
        filtered_df["candidate_id"] == candidate_search
    ]

    filtered_df = filtered_df.head(top_n)

    st.sidebar.success("Ranking file loaded successfully")

    with open(ROOT_DIR / "outputs" / "final_submission.csv", "rb") as file:
        st.sidebar.download_button(
            label="Download Final Submission CSV",
            data=file,
            file_name="final_submission.csv",
            mime="text/csv",
        )

    if filtered_df.empty:
        st.warning("No candidates found for the selected filters.")
        st.stop()

    # Candidate Leaderboard
    if "show_leaderboard" not in st.session_state:
        st.session_state.show_leaderboard = False

    def toggle_leaderboard():
        st.session_state.show_leaderboard = not st.session_state.show_leaderboard

    col1, col2 = st.columns([8, 2])

    with col1:
        section_header("Candidate Leaderboard")

    with col2:
        button_text = (
            "Hide Candidates"
            if st.session_state.show_leaderboard
            else "View Candidates"
        )

        st.button(
            button_text,
            on_click=toggle_leaderboard,
            key="leaderboard_toggle_button",
        )

    if st.session_state.show_leaderboard:
        for _, row in filtered_df.iterrows():

            score = float(row["score"])
            fit_badge = get_score_badge(score)

            candidate = get_candidate(row["candidate_id"], candidate_map)

            title = "Unknown"
            experience = "NA"

            if candidate:
                profile = candidate.get("profile", {})
                title = profile.get("current_title", "Unknown")
                experience = profile.get("years_of_experience", "NA")

            with st.container(border=True):

                card_col1, card_col2, card_col3 = st.columns([1, 4, 2])

                with card_col1:
                    st.metric("Rank", int(row["rank"]))

                with card_col2:
                    st.markdown(f"### {row['candidate_id']}")
                    st.write(f"**Role:** {title}")
                    st.write(f"**Experience:** {experience} years")

                with card_col3:
                    render_fit_box(score)
                    st.markdown(f"**{fit_badge}**")

    st.divider()

    # Candidate Deep Dive
    section_header("Candidate Deep Dive")

    selected_candidate_id = st.selectbox(
        "Select a candidate to inspect",
        filtered_df["candidate_id"].tolist(),
    )

    selected_row = df[df["candidate_id"] == selected_candidate_id].iloc[0]
    candidate = get_candidate(selected_candidate_id, candidate_map)

    if candidate:
        profile = candidate.get("profile", {})
        explanation = get_candidate_explanation(candidate, selected_row["score"])

        left, right = st.columns([1, 2])

        with left:
            st.markdown("### Candidate Snapshot")

            st.metric("Rank", int(selected_row["rank"]))
            st.write("**Fit Level:**", get_score_badge(float(selected_row["score"])))

            st.write("**Candidate ID:**", selected_candidate_id)
            st.write("**Current Title:**", profile.get("current_title", "NA"))
            st.write("**Experience:**", profile.get("years_of_experience", "NA"))
            st.write("**Location:**", profile.get("location", "NA"))
            st.write("**Country:**", profile.get("country", "NA"))

            st.markdown("### Top Skills")

            skills_html = " ".join(
                [
                    f"<span style='background-color:#E8F1FF; color:#1F4E79; padding:6px 10px; border-radius:16px; margin:4px; display:inline-block; font-size:14px;'>{skill}</span>"
                    for skill in get_top_skills(candidate)
                ]
            )

            st.markdown(skills_html, unsafe_allow_html=True)

        with right:
            st.markdown("### Hiring Recommendation")

            recommendation = explanation["recommendation"]

            if recommendation == "STRONGLY RECOMMENDED":
                st.success(recommendation)
            elif recommendation == "RECOMMENDED":
                st.info(recommendation)
            elif recommendation == "CONSIDER":
                st.warning(recommendation)
            else:
                st.error(recommendation)

            st.markdown("### Ranking Reasoning")
            st.write(selected_row["reasoning"])

            st.markdown("### Strengths")
            if explanation["strengths"]:
                for item in explanation["strengths"]:
                    st.write(f"- {item}")
            else:
                st.write("No major strengths identified.")

            st.markdown("### Risks")
            if explanation["risks"]:
                for item in explanation["risks"]:
                    st.write(f"- {item}")
            else:
                st.write("No major risks identified.")

            st.markdown("### Recruiter Summary")
            st.info(explanation["summary"])

    else:
        st.error("Candidate not found in dataset.")

    st.divider()

    # Candidate Comparison
    section_header("Candidate Comparison")

    compare_col1, compare_col2 = st.columns(2)

    candidate_options = df["candidate_id"].tolist()

    with compare_col1:
        candidate_a_id = st.selectbox(
            "Select Candidate A",
            candidate_options,
            index=0,
            key="candidate_a",
        )

    with compare_col2:
        candidate_b_id = st.selectbox(
            "Select Candidate B",
            candidate_options,
            index=1 if len(candidate_options) > 1 else 0,
            key="candidate_b",
        )

    def render_comparison_card(candidate_id):
        row = df[df["candidate_id"] == candidate_id].iloc[0]
        candidate = get_candidate(candidate_id, candidate_map)

        profile = candidate.get("profile", {})
        explanation = get_candidate_explanation(candidate, row["score"])

        st.markdown(f"### {candidate_id}")

        metric_a, metric_b = st.columns(2)

        with metric_a:
            st.metric("Score", round(float(row["score"]), 2))

        with metric_b:
            st.metric("Rank", int(row["rank"]))

        st.write("**Role:**", profile.get("current_title", "NA"))
        st.write("**Experience:**", profile.get("years_of_experience", "NA"))

        st.write("**Top Skills:**")

        skills_html = " ".join(
            [
                f"<span style='background-color:#E8F1FF; color:#1F4E79; padding:5px 9px; border-radius:14px; margin:3px; display:inline-block; font-size:13px;'>{skill}</span>"
                for skill in get_top_skills(candidate, limit=5)
            ]
        )

        st.markdown(skills_html, unsafe_allow_html=True)

        st.write("**Recommendation:**")

        recommendation = explanation["recommendation"]

        if recommendation == "STRONGLY RECOMMENDED":
            st.success(recommendation)
        elif recommendation == "RECOMMENDED":
            st.info(recommendation)
        elif recommendation == "CONSIDER":
            st.warning(recommendation)
        else:
            st.error(recommendation)

        st.write("**Main Risks:**")
        if explanation["risks"]:
            for risk in explanation["risks"][:2]:
                st.write(f"- {risk}")
        else:
            st.write("No major risks identified.")

    compare_view_col1, compare_view_col2 = st.columns(2)

    with compare_view_col1:
        with st.container(border=True):
            render_comparison_card(candidate_a_id)

    with compare_view_col2:
        with st.container(border=True):
            render_comparison_card(candidate_b_id)