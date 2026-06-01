import json

from config import (
    MUST_HAVE_SKILLS,
    NICE_TO_HAVE_SKILLS,
    NEGATIVE_KEYWORDS,
    CONSULTING_COMPANIES,
    PREFERRED_LOCATIONS,
    IDEAL_MIN_EXPERIENCE,
    IDEAL_MAX_EXPERIENCE,
)


def get_candidate_text(candidate):
    profile = candidate.get("profile", {})
    career_history = candidate.get("career_history", [])

    text_parts = [
        profile.get("headline", ""),
        profile.get("summary", ""),
        profile.get("current_title", ""),
        profile.get("current_company", ""),
        profile.get("current_industry", ""),
    ]

    for job in career_history:
        text_parts.append(job.get("title", ""))
        text_parts.append(job.get("company", ""))
        text_parts.append(job.get("industry", ""))
        text_parts.append(job.get("description", ""))

    return " ".join(text_parts).lower()


def score_candidate(candidate):
    score = 0

    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    candidate_text = get_candidate_text(candidate)

    # Skills Score
    candidate_skills = []

    for skill in candidate.get("skills", []):
        if isinstance(skill, dict):
            candidate_skills.append(skill.get("name", "").lower())
        else:
            candidate_skills.append(str(skill).lower())

    for skill in candidate_skills:
        if skill in MUST_HAVE_SKILLS:
            score += 10
        elif skill in NICE_TO_HAVE_SKILLS:
            score += 5

    # Experience Score
    experience = profile.get("years_of_experience", 0)

    if IDEAL_MIN_EXPERIENCE <= experience <= IDEAL_MAX_EXPERIENCE:
        score += 25
    elif experience > IDEAL_MAX_EXPERIENCE:
        score += 15
    elif experience >= 3:
        score += 10

    # Behavior Score
    if signals.get("open_to_work_flag"):
        score += 8

    if signals.get("recruiter_response_rate", 0) >= 0.6:
        score += 10
    elif signals.get("recruiter_response_rate", 0) >= 0.4:
        score += 5

    if signals.get("github_activity_score", -1) >= 50:
        score += 10
    elif signals.get("github_activity_score", -1) >= 20:
        score += 5

    if signals.get("interview_completion_rate", 0) >= 0.75:
        score += 8
    elif signals.get("interview_completion_rate", 0) >= 0.5:
        score += 4

    if signals.get("profile_completeness_score", 0) >= 80:
        score += 5

    if signals.get("notice_period_days", 180) <= 30:
        score += 5
    elif signals.get("notice_period_days", 180) > 90:
        score -= 8

    # Location Score
    location = profile.get("location", "").lower()
    country = profile.get("country", "").lower()

    if country == "india":
        score += 5

    for preferred_location in PREFERRED_LOCATIONS:
        if preferred_location in location:
            score += 8
            break

    if signals.get("willing_to_relocate"):
        score += 5

    # Negative Penalties
    for keyword in NEGATIVE_KEYWORDS:
        if keyword in candidate_text:
            score -= 10

    current_company = profile.get("current_company", "").lower()

    if current_company in CONSULTING_COMPANIES:
        score -= 8

    return score


def main():
    with open("data/sample_candidates.json", "r", encoding="utf-8") as f:
        candidates = json.load(f)

    ranked = []

    for candidate in candidates:
        score = score_candidate(candidate)

        ranked.append({
            "candidate_id": candidate["candidate_id"],
            "score": score
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)

    print("\nTOP 10 CANDIDATES\n")

    for i, candidate in enumerate(ranked[:10], start=1):
        print(f"{i}. {candidate['candidate_id']} -> Score: {candidate['score']}")


if __name__ == "__main__":
    main()