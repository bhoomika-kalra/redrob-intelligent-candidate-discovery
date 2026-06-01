import json

from load_candidates import load_candidates


def build_candidate_text(candidate):
    profile = candidate.get("profile", {})
    career_history = candidate.get("career_history", [])
    education = candidate.get("education", [])
    skills = candidate.get("skills", [])

    text_parts = []

    # Profile
    text_parts.append(profile.get("headline", ""))
    text_parts.append(profile.get("summary", ""))
    text_parts.append(profile.get("current_title", ""))
    text_parts.append(profile.get("current_industry", ""))

    # Career history
    for job in career_history:
        text_parts.append(job.get("title", ""))
        text_parts.append(job.get("industry", ""))
        text_parts.append(job.get("description", ""))

    # Education
    for edu in education:
        text_parts.append(edu.get("degree", ""))
        text_parts.append(edu.get("field_of_study", ""))

    # Skills
    for skill in skills:
        if isinstance(skill, dict):
            text_parts.append(skill.get("name", ""))
            text_parts.append(skill.get("proficiency", ""))
        else:
            text_parts.append(str(skill))

    return " ".join(text_parts).strip()


if __name__ == "__main__":
    candidates = load_candidates(limit=3)

    for candidate in candidates:
        print("\n" + "=" * 80)
        print(candidate["candidate_id"])
        print("=" * 80)
        print(build_candidate_text(candidate)[:1500])