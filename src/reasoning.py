from load_candidates import load_candidates
from scoring import get_score_breakdown


def get_top_skills(candidate, limit=4):
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


def generate_reasoning(candidate, score_breakdown):
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})

    years = profile.get("years_of_experience", 0)
    title = profile.get("current_title", "candidate")
    location = profile.get("location", "unknown location")

    top_skills = get_top_skills(candidate)
    skills_text = ", ".join(top_skills) if top_skills else "relevant technical skills"

    strengths = []

    strengths.append(
        f"{title} with {years} years of experience and skills in {skills_text}"
    )

    if score_breakdown.get("behavior_score", 0) >= 40:
        strengths.append("strong Redrob engagement signals")
    elif signals.get("open_to_work_flag"):
        strengths.append("open-to-work status")

    if score_breakdown.get("location_score", 0) >= 70:
        strengths.append(f"good location/logistics fit from {location}")

    concerns = []

    if signals.get("notice_period_days", 0) > 90:
        concerns.append(f"{signals.get('notice_period_days')} day notice period")

    if signals.get("recruiter_response_rate", 1) < 0.3:
        concerns.append("low recruiter response rate")

    if score_breakdown.get("skills_score", 0) < 20:
        concerns.append("limited direct retrieval/ranking skill evidence")

    if score_breakdown.get("skills_score", 0) >= 30:
        reasoning = "Strong match for the Senior AI Engineer role as a " + strengths[0]
    elif score_breakdown.get("skills_score", 0) >= 15:
        reasoning = "Moderate match for the Senior AI Engineer role as a " + strengths[0]
    else:
        reasoning = "Potentially weak match for the Senior AI Engineer role as a " + strengths[0]

    if len(strengths) > 1:
        reasoning += ", with " + ", ".join(strengths[1:])

    reasoning += "."

    if concerns:
        reasoning += " Concern: " + "; ".join(concerns[:2]) + "."

    return reasoning


if __name__ == "__main__":
    candidates = load_candidates(limit=5)

    for candidate in candidates:
        breakdown = get_score_breakdown(candidate)
        print("\nCandidate:", candidate["candidate_id"])
        print(generate_reasoning(candidate, breakdown))
        