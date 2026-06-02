from load_candidates import load_candidates
from scoring import get_score_breakdown
from career_intelligence import score_career_fit
from retrieval_intelligence import score_retrieval_intelligence


def get_top_skills(candidate, limit=5):
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


def generate_strengths(candidate, breakdown):
    strengths = []

    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})

    title = profile.get("current_title", "")
    experience = profile.get("years_of_experience", 0)

    positive_title_keywords = [
        "ai", "ml", "machine learning", "data scientist",
        "software engineer", "backend engineer", "data engineer",
        "research engineer", "search engineer", "recommendation"
    ]

    if title and any(keyword in title.lower() for keyword in positive_title_keywords):
        strengths.append(f"Current role is {title}")

    if 5 <= experience <= 9:
        strengths.append(f"{experience} years of experience fits the preferred seniority range")

    top_skills = get_top_skills(candidate)
    relevant_skills = [
        skill for skill in top_skills
        if skill.lower() in [
            "python", "machine learning", "deep learning", "nlp", "llm",
            "rag", "faiss", "milvus", "qdrant", "pinecone", "weaviate",
            "semantic search", "vector search", "learning to rank",
            "elasticsearch", "opensearch", "bm25", "fine-tuning llms",
            "lora", "qlora", "peft"
        ]
    ]

    if relevant_skills:
        strengths.append("Strong AI/retrieval skill evidence in " + ", ".join(relevant_skills[:4]))

    if breakdown.get("career_fit_score", 0) >= 70:
        strengths.append("Career history strongly aligns with AI/ML or search-oriented roles")

    if breakdown.get("retrieval_intelligence_score", 0) >= 50:
        strengths.append("Shows strong retrieval/search/recommendation system signals")

    if signals.get("open_to_work_flag"):
        strengths.append("Open to work signal indicates higher availability")

    if signals.get("recruiter_response_rate", 0) >= 0.6:
        strengths.append("Good recruiter response rate")

    if signals.get("github_activity_score", 0) >= 50:
        strengths.append("Strong GitHub activity signal")

    return strengths[:6]


def generate_risks(candidate, breakdown):
    risks = []

    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})

    experience = profile.get("years_of_experience", 0)
    title = profile.get("current_title", "").lower()

    if experience < 5:
        risks.append("Experience is below the preferred 5–9 year range")

    if signals.get("notice_period_days", 0) > 90:
        risks.append(f"Long notice period of {signals.get('notice_period_days')} days")

    if signals.get("recruiter_response_rate", 1) < 0.3:
        risks.append("Low recruiter response rate")

    if breakdown.get("retrieval_intelligence_score", 0) < 30:
        risks.append("Limited evidence of production retrieval or ranking systems")

    if "junior" in title:
        risks.append("Current title suggests junior seniority")

    if breakdown.get("penalty_score", 0) < -20:
        risks.append("Profile has negative fit signals based on role or career background")

    return risks[:4]


def generate_hiring_recommendation(final_score):
    if final_score >= 75:
        return "STRONGLY RECOMMENDED"
    if final_score >= 60:
        return "RECOMMENDED"
    if final_score >= 45:
        return "CONSIDER"
    return "LOW PRIORITY"


def generate_explanation(candidate, breakdown, final_score):
    profile = candidate.get("profile", {})

    candidate_id = candidate.get("candidate_id", "")
    title = profile.get("current_title", "Unknown role")
    experience = profile.get("years_of_experience", 0)

    strengths = generate_strengths(candidate, breakdown)
    risks = generate_risks(candidate, breakdown)
    recommendation = generate_hiring_recommendation(final_score)

    explanation = {
        "candidate_id": candidate_id,
        "title": title,
        "experience": experience,
        "recommendation": recommendation,
        "strengths": strengths,
        "risks": risks,
        "summary": (
            f"{recommendation}: {title} with {experience} years of experience. "
            f"Strengths include {', '.join(strengths[:3]) if strengths else 'relevant profile signals'}. "
            f"Risks include {', '.join(risks[:2]) if risks else 'no major concerns identified'}."
        )
    }

    return explanation


if __name__ == "__main__":
    candidates = load_candidates(limit=5)

    for candidate in candidates:
        breakdown = get_score_breakdown(candidate)
        breakdown["career_fit_score"] = score_career_fit(candidate)
        breakdown["retrieval_intelligence_score"] = score_retrieval_intelligence(candidate)

        print("\n" + "=" * 80)
        print(generate_explanation(candidate, breakdown, 50))