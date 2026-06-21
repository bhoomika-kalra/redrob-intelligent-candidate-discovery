import sys
from pathlib import Path

import streamlit as st
from PIL import Image
import html
import streamlit.components.v1 as components

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

st.sidebar.markdown(
    """
    <h2 style="
        margin-bottom:20px;
        font-weight:800;
        color:#1F2937;
    ">
        DASHBOARD
    </h2>
    """,
    unsafe_allow_html=True,
)

if "page" not in st.session_state:
    st.session_state.page = "Dashboard Overview"


def go_dashboard():
    st.session_state.page = "Dashboard Overview"


def go_explorer():
    st.session_state.page = "Candidate Explorer"


st.sidebar.button(
    "Dashboard Overview",
    use_container_width=True,
    type="primary" if st.session_state.page == "Dashboard Overview" else "secondary",
    on_click=go_dashboard,
    key="nav_dashboard",
)

st.sidebar.button(
    "Candidate Explorer",
    use_container_width=True,
    type="primary" if st.session_state.page == "Candidate Explorer" else "secondary",
    on_click=go_explorer,
    key="nav_explorer",
)

page = st.session_state.page

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
    
    section[data-testid="stSidebar"] button {
        border-radius: 12px !important;
        border: 1px solid #D1D5DB !important;
        background-color: white !important;
        color: #1F2937 !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] button:hover {
        border: 1px solid #6D28D9 !important;
        color: #6D28D9 !important;
        background-color: #F5F3FF !important;
    }

    section[data-testid="stSidebar"] button:focus {
        border: 1px solid #6D28D9 !important;
        box-shadow: none !important;
        outline: none !important;
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
        logo = logo.resize((150, 150))

        st.image(logo)

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

    # ===RECRUITER OVERVIEW===
    section_header("Recruiter Overview")

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    metric_col1.metric("Top Score", metrics["top_score"])
    metric_col2.metric("Average Score", metrics["avg_score"])
    metric_col3.metric("Candidates Ranked", metrics["total_ranked"])
    metric_col4.metric("Lowest Score", metrics["lowest_score"])

    st.divider()

    # ===RECRUITER INSIGHTS===
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

    # ===TOP TALENT PICKS===
    section_header("Top Talent Picks")

    top_3 = df.head(3)

    cards_html = ""

    for idx, (_, row) in enumerate(top_3.iterrows()):
        candidate = get_candidate(row["candidate_id"], candidate_map)
        profile = candidate.get("profile", {}) if candidate else {}

        title = profile.get("current_title", "Unknown")
        experience = profile.get("years_of_experience", "NA")
        score = round(float(row["score"]), 2)
        fit = get_score_badge(score)

        active_class = "active" if idx == 0 else ""

        cards_html += f"""
        <div class="option {active_class}">
            <div class="shadow"></div>
            <div class="label">
                <div class="rank">Rank {int(row['rank'])}</div>
                <div class="info">
                    <div class="main">{row['candidate_id']}</div>
                    <div class="sub">{title}</div>
                    <div class="sub">Experience: {experience} years</div>
                    <div class="score">Score: {score}</div>
                    <div class="fit">{fit}</div>
                </div>
            </div>
        </div>
        """

    components.html(
        f"""
        <style>
        .options {{
            display:flex;
            gap:18px;
            width:100%;
            height:360px;
            overflow:hidden;
            font-family:Arial, sans-serif;
        }}

        .option {{
            position:relative;
            flex:0.8;
            border-radius:32px;
            background:linear-gradient(135deg,#1E3A8A,#6D28D9);
            cursor:pointer;
            transition:all .55s cubic-bezier(0.05, 0.61, 0.41, 0.95);
            overflow:hidden;
            color:white;
            box-shadow:0 8px 24px rgba(0,0,0,0.12);
            min-width:90px;
        }}

        .option:nth-child(2) {{
            background:linear-gradient(135deg,#4338CA,#7C3AED);
        }}

        .option:nth-child(3) {{
            background:linear-gradient(135deg,#2563EB,#1E40AF);
        }}

        .option.active {{
            flex:4;
            border-radius:36px;
        }}

        .option:not(.active) {{
            flex:0.55;
            border-radius:999px;
        }}

        .option:not(.active) .info {{
            opacity:0;
            transform:translateX(40px);
            pointer-events:none;
        }}

        .option:not(.active) .rank {{
            position:absolute;
            bottom:24px;
            left:50%;
            transform:translateX(-50%);
            white-space:nowrap;
        }}

        .shadow {{
            position:absolute;
            inset:0;
            background:linear-gradient(to top,rgba(0,0,0,.45),rgba(0,0,0,.05));
        }}

        .label {{
            position:absolute;
            top:45px;
            bottom:45px;
            left:36px;
            right:36px;
            z-index:2;
            display:flex;
            flex-direction:column;
            justify-content:space-between;
        }}

        .rank {{
            background:white;
            color:#6D28D9;
            display:inline-block;
            padding:7px 16px;
            border-radius:999px;
            font-weight:700;
            margin-bottom:18px;
            transition:all .45s ease;
        }}

        .info {{
            transition:all .45s ease;
        }}

        .main {{
            font-size:42px;
            font-weight:800;
            margin-bottom:12px;
        }}

        .sub {{
            font-size:18px;
            margin-bottom:8px;
        }}

        .score {{
            margin-top:20px;
            font-size:30px;
            font-weight:800;
        }}

        .fit {{
            margin-top:8px;
            font-size:17px;
            font-weight:700;
        }}
        </style>

        <div class="options">
            {cards_html}
        </div>

        <script>
        const cards = document.querySelectorAll(".option");
        cards.forEach(card => {{
            card.addEventListener("click", () => {{
                cards.forEach(c => c.classList.remove("active"));
                card.classList.add("active");
            }});
        }});
        </script>
        """,
        height=390,
    )

    st.divider()

    # ===RANKING ANALYTICS===
    section_header("Ranking Analytics")

    top_chart_df = df.head(10)
    max_score = top_chart_df["score"].max()

    bars_html = ""

    for _, row in top_chart_df.iterrows():
        score = round(float(row["score"]), 1)
        height = int((score / max_score) * 260)

        bars_html += f"""
        <div class="bar-item">
            <div class="bar" style="height:{height}px;">
                <span>{score}</span>
            </div>
            <div class="bar-label">{row['candidate_id']}</div>
        </div>
        """

    score_bins = {
        "20-30": len(df[(df["score"] >= 20) & (df["score"] < 30)]),
        "30-40": len(df[(df["score"] >= 30) & (df["score"] < 40)]),
        "40-50": len(df[(df["score"] >= 40) & (df["score"] < 50)]),
        "50-60": len(df[(df["score"] >= 50) & (df["score"] < 60)]),
        "60-70": len(df[(df["score"] >= 60) & (df["score"] < 70)]),
        "70+": len(df[df["score"] >= 70]),
    }

    max_count = max(score_bins.values())
    dist_html = ""

    for label, count in score_bins.items():
        height = int((count / max_count) * 260) if max_count else 0

        dist_html += f"""
        <div class="bar-item">
            <div class="bar secondary" style="height:{height}px;">
                <span>{count}</span>
            </div>
            <div class="bar-label">{label}</div>
        </div>
        """

    components.html(
        f"""
        <style>
        .analytics-grid {{
            display:grid;
            grid-template-columns:1fr;
            gap:28px;
            width:100%;
            font-family:Arial, sans-serif;
        }}

        .chart-card {{
            background:linear-gradient(135deg,#1E3A8A,#6D28D9);
            border-radius:28px;
            padding:30px;
            height:430px;
            color:white;
            box-shadow:0 10px 30px rgba(0,0,0,0.15);
            overflow:hidden;
        }}

        .chart-card.secondary-card {{
            background:linear-gradient(135deg,#2563EB,#1E3A8A);
        }}

        .chart-title {{
            font-size:24px;
            font-weight:800;
            margin-bottom:30px;
        }}

        .bar-wrap {{
            display:flex;
            align-items:flex-end;
            justify-content:space-between;
            gap:18px;
            height:300px;
        }}

        .bar-item {{
            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:flex-end;
            height:100%;
            flex:1;
        }}

        .bar {{
            width:48px;
            background:white;
            border-radius:8px 8px 0 0;
            position:relative;
            box-shadow:10px 12px 0 rgba(0,0,0,0.18);
            transform-origin:bottom;
            animation:barRise 1.2s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        }}

        .bar.secondary {{
            background:#EDE9FE;
        }}

        .bar-item:nth-child(1) .bar {{ animation-delay:0.1s; }}
        .bar-item:nth-child(2) .bar {{ animation-delay:0.2s; }}
        .bar-item:nth-child(3) .bar {{ animation-delay:0.3s; }}
        .bar-item:nth-child(4) .bar {{ animation-delay:0.4s; }}
        .bar-item:nth-child(5) .bar {{ animation-delay:0.5s; }}
        .bar-item:nth-child(6) .bar {{ animation-delay:0.6s; }}
        .bar-item:nth-child(7) .bar {{ animation-delay:0.7s; }}
        .bar-item:nth-child(8) .bar {{ animation-delay:0.8s; }}

        .bar span {{
            position:absolute;
            top:-28px;
            left:50%;
            transform:translateX(-50%);
            font-weight:800;
            color:white;
            font-size:15px;
        }}

        .bar-label {{
            margin-top:18px;
            font-size:10px;
            width:70px;
            text-align:center;
            color:white;
            opacity:0.95;
            transform:rotate(-18deg);
        }}

        @keyframes barRise {{
            0% {{
                transform:scaleY(0);
                opacity:0;
            }}
            70% {{
                transform:scaleY(1.08);
                opacity:1;
            }}
            100% {{
                transform:scaleY(1);
                opacity:1;
            }}
        }}
        </style>

        <div class="analytics-grid">
            <div class="chart-card">
                <div class="chart-title">Top 10 Candidates Scores</div>
                <div class="bar-wrap">
                    {bars_html}
                </div>
            </div>

            <div class="chart-card secondary-card">
                <div class="chart-title">Candidate Score Distribution</div>
                <div class="bar-wrap">
                    {dist_html}
                </div>
            </div>
        </div>
        """,
        height=1050,
    )

# =========================
# PAGE 2: CANDIDATE EXPLORER
# =========================
elif page == "Candidate Explorer":

    # === CANDIDATE CONTROLS SIDEBAR ===

    st.sidebar.markdown(
        """
        <div style="
            background:white;
            padding:18px;
            border-radius:16px;
            border:1px solid #E5E7EB;
            margin-bottom:18px;
        ">
            <h2 style="margin:0;color:#1F2937;">Candidate Controls</h2>
            <p style="margin:6px 0 0 0;color:#6B7280;font-size:14px;">
                Explore ranked candidates and inspect profiles.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("#### Filters")

    top_n = st.sidebar.slider(
        "Top Candidates to Display",
        min_value=10,
        max_value=100,
        value=25,
        step=5,
    )

    min_score = st.sidebar.slider(
        "Minimum Match Score",
        min_value=float(df["score"].min()),
        max_value=float(df["score"].max()),
        value=float(df["score"].min()),
    )

    st.sidebar.divider()

    st.sidebar.markdown("#### Search on Leaderboard")

    role_filter = st.sidebar.text_input(
        "Role / Skill Search",
        placeholder="AI Engineer, NLP, FAISS..."
    )

    candidate_search = st.sidebar.selectbox(
        "Search Candidate",
        ["Select Candidate"] + df["candidate_id"].tolist()
    )

    # Filter only for Candidate Leaderboard
    leaderboard_df = df[df["score"] >= min_score]

    if role_filter:
        leaderboard_df = leaderboard_df[
            leaderboard_df["reasoning"]
            .str.lower()
            .str.contains(role_filter.lower(), na=False)
        ]

    if candidate_search != "Select Candidate":
        leaderboard_df = leaderboard_df[
            leaderboard_df["candidate_id"] == candidate_search
        ]

    leaderboard_df = leaderboard_df.head(top_n)

    # Full data for Deep Dive and Comparison
    deep_dive_df = df.copy()
    comparison_df = df.copy()

    st.sidebar.divider()

    st.sidebar.caption("Ranking data loaded")

    with open(ROOT_DIR / "outputs" / "final_submission.csv", "rb") as file:
        st.sidebar.download_button(
            label="Download Ranked Candidates",
            data=file,
            file_name="final_submission.csv",
            mime="text/csv",
            use_container_width=True,
        )

    if leaderboard_df.empty:
        st.warning("No candidates found for the selected filters.")
        st.stop()

    # ===CANDIDATE LEADERBOARD===
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
        
        items_per_page = 10

        if "leaderboard_page" not in st.session_state:
            st.session_state.leaderboard_page = 0

        total_candidates = len(leaderboard_df)

        total_pages = max(
            1,
            (total_candidates + items_per_page - 1) // items_per_page
        )

        # Safety check
        if st.session_state.leaderboard_page >= total_pages:
            st.session_state.leaderboard_page = total_pages - 1

        start_idx = st.session_state.leaderboard_page * items_per_page
        end_idx = start_idx + items_per_page

        page_df = leaderboard_df.iloc[start_idx:end_idx]
        rows_html = ""

        for _, row in page_df.iterrows():

            score = round(float(row["score"]), 2)
            candidate = get_candidate(row["candidate_id"], candidate_map)

            title = "Unknown"
            experience = "NA"

            if candidate:
                profile = candidate.get("profile", {})
                title = profile.get("current_title", "Unknown")
                experience = profile.get("years_of_experience", "NA")

            if score >= 75:
                status = "Strong Fit"
                status_color = "#22C55E"
            elif score >= 50:
                status = "Good Fit"
                status_color = "#F59E0B"
            else:
                status = "Review"
                status_color = "#EF4444"

            rows_html += f"""
            <tr>
                <td>
                    <div class="main-text">{int(row['rank'])}</div>
                    <div class="sub-text">Rank</div>
                </td>
                <td>
                    <a 
                        href="?deep_candidate={row['candidate_id']}#candidate-deep-dive"
                        target="_parent"
                        class="candidate-link"
                    >
                        <div class="main-text">{row['candidate_id']}</div>
                        <div class="sub-text">Candidate ID</div>
                    </a>
                </td>
                <td>
                    <div class="main-text">{title}</div>
                    <div class="sub-text">Role</div>
                </td>
                <td>
                    <div class="main-text">{experience} years</div>
                    <div class="sub-text">Experience</div>
                </td>
                <td>
                    <div class="main-text">{score}</div>
                    <div class="sub-text">Score</div>
                </td>
                <td>
                    <div class="status-cell">
                        <span class="status-dot" style="border-color:{status_color};"></span>
                        <span>{status}</span>
                    </div>
                </td>
            </tr>
            """

        leaderboard_height = (len(leaderboard_df) * 74) + 95

        components.html(
            f"""
            <style>
            body {{
                margin:0;
                padding:0;
                background:transparent;
            }}

            .leaderboard-card {{
                background:white;
                border:1px solid #E5E7EB;
                border-radius:20px;
                overflow-y:auto;
                max-height:1300px;
                box-shadow:0 8px 24px rgba(37,99,235,0.08);
                font-family:Arial, sans-serif;
            }}

            table {{
                width:100%;
                border-collapse:collapse;
            }}

            thead {{
                background:linear-gradient(135deg,#2563EB,#6D28D9);
            }}

            th {{
                text-align:left;
                padding:16px 22px;
                font-size:15px;
                color:white;
                font-weight:700;
            }}

            td {{
                padding:14px 22px;
                border-bottom:1px solid #E5E7EB;
                font-size:15px;
                vertical-align:middle;
                color:#1F2937;
            }}

            tr:hover {{
                background:#F5F3FF;
                cursor:pointer;
            }}

            .main-text {{
                font-size:16px;
                font-weight:700;
                color:#111827;
                line-height:1.2;
            }}

            .sub-text {{
                font-size:13px;
                color:#6B7280;
                margin-top:4px;
                line-height:1.2;
            }}

            .status-cell {{
                display:flex;
                align-items:center;
                gap:10px;
                color:#111827;
                font-weight:700;
            }}

            .status-dot {{
                display:inline-block;
                width:13px;
                height:13px;
                border-radius:50%;
                border:4px solid;
            }}
            
            .candidate-link {{
                text-decoration:none;
                color:inherit;
                display:block;
            }}

            .candidate-link:hover .main-text {{
                color:#6D28D9;
            }}
            </style>

            <div class="leaderboard-card">
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Candidate</th>
                            <th>Role</th>
                            <th>Experience</th>
                            <th>Score</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
            """,
            height=(len(page_df) * 65) + 120,
        )
        
        start_show = start_idx + 1
        end_show = min(end_idx, total_candidates)
        
        st.markdown(
            f"""
            <div style="
                text-align:center;
                color:#6B7280;
                font-size:14px;
                margin-bottom:10px;
            ">
                Showing {start_show}-{end_show} of {total_candidates}
            </div>
            """,
            unsafe_allow_html=True,
        )

        left_space, prev_col, page_col, next_col, right_space = st.columns(
            [3, 1, 1, 1, 3]
        )

        with prev_col:
            if st.button(
                "‹ Prev",
                disabled=st.session_state.leaderboard_page == 0,
                key="prev_page",
                use_container_width=True,
            ):
                st.session_state.leaderboard_page -= 1
                st.rerun()

        with page_col:
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    font-size:18px;
                    font-weight:700;
                    padding-top:8px;
                ">
                    {st.session_state.leaderboard_page + 1}/{total_pages}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with next_col:
            if st.button(
                "Next ›",
                disabled=st.session_state.leaderboard_page >= total_pages - 1,
                key="next_page",
                use_container_width=True,
            ):
                st.session_state.leaderboard_page += 1
                st.rerun()
                    
    st.divider()
    
    # ===CANDIDATE DEEP DIVE===
    st.markdown('<div id="candidate-deep-dive"></div>', unsafe_allow_html=True)
    section_header("Candidate Deep Dive")

    deep_candidate_options = deep_dive_df["candidate_id"].tolist()
    deep_candidate_from_url = st.query_params.get("deep_candidate", None)

    if deep_candidate_from_url in deep_candidate_options:
        st.session_state.deep_dive_candidate = deep_candidate_from_url

    if "deep_dive_candidate" not in st.session_state:
        st.session_state.deep_dive_candidate = deep_candidate_options[0]

    selected_candidate_id = st.selectbox(
        "Select a Candidate for Deep Analysis",
        deep_candidate_options,
        key="deep_dive_candidate",
    )

    selected_row = df[df["candidate_id"] == selected_candidate_id].iloc[0]
    candidate = get_candidate(selected_candidate_id, candidate_map)

    if candidate:
        profile = candidate.get("profile", {})
        explanation = get_candidate_explanation(candidate, selected_row["score"])

        score = round(float(selected_row["score"]), 2)
        rank = int(selected_row["rank"])

        title = profile.get("current_title", "NA")
        experience = profile.get("years_of_experience", "NA")
        location = profile.get("location", "NA")
        country = profile.get("country", "NA")

        recommendation = explanation["recommendation"]

        if recommendation == "STRONGLY RECOMMENDED":
            rec_color = "#22C55E"
            rec_bg = "#ECFDF5"
        elif recommendation == "RECOMMENDED":
            rec_color = "#2563EB"
            rec_bg = "#EFF6FF"
        elif recommendation == "CONSIDER":
            rec_color = "#F59E0B"
            rec_bg = "#FFFBEB"
        else:
            rec_color = "#EF4444"
            rec_bg = "#FEF2F2"

        skills_html = "".join(
            [
                f"<span class='skill-pill'>{html.escape(str(skill))}</span>"
                for skill in get_top_skills(candidate)
            ]
        )

        strengths_html = "".join(
            [
                f"<li>{html.escape(str(item))}</li>"
                for item in explanation["strengths"]
            ]
        ) or "<li>No major strengths identified.</li>"

        risks_html = "".join(
            [
                f"<li>{html.escape(str(item))}</li>"
                for item in explanation["risks"]
            ]
        ) or "<li>No major risks identified.</li>"

        components.html(
            f"""
            <style>
            .deep-card-wrapper {{
                font-family: Arial, sans-serif;
                display: grid;
                grid-template-columns: 0.9fr 1.5fr;
                gap: 28px;
                width: 100%;
            }}

            .profile-card, .intel-card {{
                background: white;
                border-radius: 24px;
                border: 1px solid #E5E7EB;
                box-shadow: 0 12px 30px rgba(37,99,235,0.08);
                overflow: hidden;
                animation: fadeUp 0.7s ease;
            }}

            .profile-header {{
                background: linear-gradient(135deg, #2563EB, #6D28D9);
                padding: 32px;
                color: white;
                position: relative;
                overflow: hidden;
            }}

            .profile-header::before {{
                content: "";
                position: absolute;
                width: 220px;
                height: 220px;
                border-radius: 50%;
                background: rgba(255,255,255,0.12);
                right: -70px;
                top: -80px;
            }}

            .avatar {{
                width: 82px;
                height: 82px;
                border-radius: 50%;
                background: white;
                color: #6D28D9;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 30px;
                font-weight: 800;
                margin-bottom: 18px;
                position: relative;
                z-index: 2;
            }}

            .candidate-id {{
                font-size: 28px;
                font-weight: 800;
                margin-bottom: 8px;
                position: relative;
                z-index: 2;
            }}

            .candidate-title {{
                font-size: 18px;
                opacity: 0.9;
                position: relative;
                z-index: 2;
                font-style: italic;
            }}

            .profile-body {{
                padding: 26px;
            }}

            .detail-item {{
                padding: 15px 16px;
                border-radius: 16px;
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                margin-bottom: 12px;
                transition: all 0.3s ease;
            }}

            .detail-item:hover {{
                transform: translateX(6px);
                background: #F5F3FF;
            }}

            .detail-label {{
                font-size: 12px;
                color: #6B7280;
                font-weight: 700;
                text-transform: uppercase;
                margin-bottom: 5px;
            }}

            .detail-value {{
                font-size: 15px;
                color: #111827;
                font-weight: 700;
            }}

            .skills-title {{
                font-size: 20px;
                font-weight: 800;
                margin: 24px 0 14px;
                color: #111827;
            }}

            .skill-pill {{
                display: inline-block;
                background: #EDE9FE;
                color: #5B21B6;
                padding: 8px 12px;
                border-radius: 999px;
                font-size: 13px;
                font-weight: 700;
                margin: 5px;
            }}

            .intel-card {{
                padding: 30px;
            }}

            .intel-title {{
                font-size: 28px;
                font-weight: 800;
                color: #111827;
                margin-bottom: 18px;
            }}

            .recommendation-box {{
                background: {rec_bg};
                color: {rec_color};
                border-left: 6px solid {rec_color};
                padding: 18px 20px;
                border-radius: 16px;
                font-size: 17px;
                font-weight: 800;
                margin-bottom: 26px;
            }}

            .section-box {{
                background: #F8FAFC;
                border: 1px solid #E5E7EB;
                border-radius: 18px;
                padding: 20px;
                margin-bottom: 18px;
            }}

            .section-title {{
                font-size: 20px;
                font-weight: 800;
                color: #111827;
                margin-bottom: 12px;
            }}

            .section-text {{
                font-size: 15px;
                line-height: 1.7;
                color: #374151;
            }}

            ul {{
                padding-left: 20px;
                margin: 0;
            }}

            li {{
                margin-bottom: 10px;
                color: #374151;
                line-height: 1.6;
            }}

            .summary-box {{
                background: linear-gradient(135deg, #EEF2FF, #F5F3FF);
                color: #1E3A8A;
                padding: 20px;
                border-radius: 18px;
                font-size: 15px;
                line-height: 1.7;
                font-weight: 600;
            }}

            @keyframes fadeUp {{
                from {{
                    opacity: 0;
                    transform: translateY(24px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            </style>

            <div class="deep-card-wrapper">

                <div class="profile-card">
                    <div class="profile-header">
                        <div class="avatar">{rank}</div>
                        <div class="candidate-id">{html.escape(selected_candidate_id)}</div>
                        <div class="candidate-title">{html.escape(str(title))}</div>
                    </div>

                    <div class="profile-body">
                            <div class="detail-item">
                                <div class="detail-label">Score</div>
                                <div class="detail-value">{score}</div>
                            </div>

                        <div class="detail-item">
                            <div class="detail-label">Experience</div>
                            <div class="detail-value">{html.escape(str(experience))} years</div>
                        </div>

                        <div class="detail-item">
                            <div class="detail-label">Location</div>
                            <div class="detail-value">{html.escape(str(location))}</div>
                        </div>

                        <div class="detail-item">
                            <div class="detail-label">Country</div>
                            <div class="detail-value">{html.escape(str(country))}</div>
                        </div>

                        <div class="skills-title">Top Skills</div>
                        <div>{skills_html}</div>
                    </div>
                </div>

                <div class="intel-card">

                    <div class="recommendation-box">
                        {html.escape(str(recommendation))}
                    </div>

                    <div class="section-box">
                        <div class="section-title">Ranking Reasoning</div>
                        <div class="section-text">
                            {html.escape(str(selected_row["reasoning"]))}
                        </div>
                    </div>

                    <div class="section-box">
                        <div class="section-title">Strengths</div>
                        <ul>{strengths_html}</ul>
                    </div>

                    <div class="section-box">
                        <div class="section-title">Risks</div>
                        <ul>{risks_html}</ul>
                    </div>

                    <div class="section-title">Recruiter Summary</div>
                    <div class="summary-box">
                        {html.escape(str(explanation["summary"]))}
                    </div>
                </div>

            </div>
            """,
            height=980,
        )

    else:
        st.error("Candidate not found in dataset.")

    st.divider()

    # ===CANDIDATE COMPARISON===
    section_header("Candidate Comparison")

    candidate_options = df["candidate_id"].tolist()

    compare_col1, compare_col2 = st.columns(2)

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


    def build_comparison_card(candidate_id, label):
        row = df[df["candidate_id"] == candidate_id].iloc[0]
        candidate = get_candidate(candidate_id, candidate_map)

        profile = candidate.get("profile", {}) if candidate else {}
        explanation = get_candidate_explanation(candidate, row["score"])

        score = round(float(row["score"]), 2)
        rank = int(row["rank"])
        title = profile.get("current_title", "NA")
        experience = profile.get("years_of_experience", "NA")

        recommendation = explanation["recommendation"]

        if recommendation == "STRONGLY RECOMMENDED":
            rec_color = "#22C55E"
            rec_bg = "#ECFDF5"
        elif recommendation == "RECOMMENDED":
            rec_color = "#2563EB"
            rec_bg = "#EFF6FF"
        elif recommendation == "CONSIDER":
            rec_color = "#F59E0B"
            rec_bg = "#FFFBEB"
        else:
            rec_color = "#EF4444"
            rec_bg = "#FEF2F2"

        skills_html = "".join(
            [
                f"<span class='cmp-skill'>{html.escape(str(skill))}</span>"
                for skill in get_top_skills(candidate, limit=5)
            ]
        )

        risks = explanation["risks"][:2]
        risks_html = "".join(
            [f"<li>{html.escape(str(risk))}</li>" for risk in risks]
        ) or "<li>No major risks identified.</li>"

        return f"""
        <div class="comparison-card">

            <div class="comparison-header">
                <div>
                    <div class="candidate-label">{label}</div>
                    <div class="candidate-name">{html.escape(candidate_id)}</div>
                    <div class="candidate-role">{html.escape(str(title))}</div>
                </div>

                <div class="rank-badge">{rank}</div>
            </div>

            <div class="metric-row">
                <div class="metric-box">
                    <div class="metric-label">Score</div>
                    <div class="metric-value">{score}</div>
                </div>

                <div class="metric-box">
                    <div class="metric-label">Experience</div>
                    <div class="metric-value">{html.escape(str(experience))} yrs</div>
                </div>
            </div>

            <div class="info-block">
                <div class="block-title">Top Skills</div>
                <div>{skills_html}</div>
            </div>

            <div class="recommendation-pill" style="background:{rec_bg}; color:{rec_color}; border-left:5px solid {rec_color};">
                {html.escape(str(recommendation))}
            </div>

            <div class="info-block">
                <div class="block-title">Main Risks</div>
                <ul>{risks_html}</ul>
            </div>

        </div>
        """


    card_a = build_comparison_card(candidate_a_id, "Candidate A")
    card_b = build_comparison_card(candidate_b_id, "Candidate B")

    components.html(
        f"""
        <style>
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: Arial, sans-serif;
        }}

        .comparison-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 26px;
            width: 100%;
        }}

        .comparison-card {{
            background: white;
            border: 1px solid #E5E7EB;
            border-radius: 24px;
            overflow: hidden;
            box-shadow: 0 12px 30px rgba(37,99,235,0.08);
            animation: fadeUp 0.6s ease;
        }}

        .comparison-card:hover {{
            transform: translateY(-4px);
            transition: 0.3s ease;
            box-shadow: 0 18px 40px rgba(109,40,217,0.12);
        }}

        .comparison-header {{
            background: linear-gradient(135deg, #2563EB, #6D28D9);
            color: white;
            padding: 26px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            position: relative;
            overflow: hidden;
        }}

        .comparison-header::after {{
            content: "";
            position: absolute;
            width: 170px;
            height: 170px;
            border-radius: 50%;
            right: -55px;
            top: -65px;
            background: rgba(255,255,255,0.12);
        }}

        .candidate-label {{
            display: inline-block;
            background: rgba(255,255,255,0.18);
            padding: 6px 12px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 800;
            margin-bottom: 14px;
        }}

        .candidate-name {{
            font-size: 28px;
            font-weight: 900;
            margin-bottom: 8px;
            position: relative;
            z-index: 2;
        }}

        .candidate-role {{
            font-size: 15px;
            opacity: 0.92;
            position: relative;
            z-index: 2;
        }}

        .rank-badge {{
            width: 68px;
            height: 68px;
            border-radius: 50%;
            background: white;
            color: #6D28D9;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: 900;
            position: relative;
            z-index: 2;
        }}

        .metric-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
            padding: 24px 24px 10px;
        }}

        .metric-box {{
            background: #F8FAFC;
            border: 1px solid #E5E7EB;
            border-radius: 16px;
            padding: 16px;
        }}

        .metric-label {{
            color: #6B7280;
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
            margin-bottom: 6px;
        }}

        .metric-value {{
            color: #111827;
            font-size: 24px;
            font-weight: 900;
        }}

        .info-block {{
            padding: 14px 24px;
        }}

        .block-title {{
            color: #111827;
            font-size: 16px;
            font-weight: 900;
            margin-bottom: 12px;
        }}

        .cmp-skill {{
            display: inline-block;
            background: #EDE9FE;
            color: #5B21B6;
            padding: 8px 12px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 700;
            margin: 4px;
        }}

        .recommendation-pill {{
            margin: 18px 24px;
            padding: 16px 18px;
            border-radius: 16px;
            font-size: 15px;
            font-weight: 900;
        }}

        ul {{
            margin: 0;
            padding-left: 20px;
            color: #374151;
            line-height: 1.6;
        }}

        li {{
            margin-bottom: 8px;
        }}

        @keyframes fadeUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        </style>

        <div class="comparison-grid">
            {card_a}
            {card_b}
        </div>
        """,
        height=650,
    )