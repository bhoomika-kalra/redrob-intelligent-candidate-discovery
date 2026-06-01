import sys
import os
from typing import Dict, Any

# Ensure the current directory is in python path to resolve imports correctly when run from different directories
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import (
    MUST_HAVE_SKILLS,
    NICE_TO_HAVE_SKILLS,
    NEGATIVE_KEYWORDS,
    CONSULTING_COMPANIES,
    PREFERRED_LOCATIONS,
    IDEAL_MIN_EXPERIENCE,
    IDEAL_MAX_EXPERIENCE,
)
from build_candidate_text import build_candidate_text
from load_candidates import load_candidates


def score_skills(candidate: Dict[str, Any]) -> float:
    """
    Score candidate skills based on MUST_HAVE_SKILLS and NICE_TO_HAVE_SKILLS.
    Each skill object has name, proficiency, endorsements, duration_months.
    - Must-have skills get a higher score.
    - Nice-to-have skills get a smaller score.
    - Expert/advanced proficiency gets a bonus.
    - High endorsements get a bonus.
    - Longer duration_months gets a bonus.
    """
    score = 0.0
    skills = candidate.get("skills", [])
    if not skills:
        return score
    
    # Pre-process config skills for fast matching
    must_haves = {s.lower().strip() for s in MUST_HAVE_SKILLS}
    nice_to_haves = {s.lower().strip() for s in NICE_TO_HAVE_SKILLS}

    for skill in skills:
        if isinstance(skill, dict):
            name = (skill.get("name") or "").lower().strip()
            proficiency = (skill.get("proficiency") or "").lower().strip()
            endorsements = skill.get("endorsements") or 0
            duration = skill.get("duration_months") or 0
        else:
            name = str(skill or "").lower().strip()
            proficiency = ""
            endorsements = 0
            duration = 0
        
        if not name:
            continue
            
        skill_score = 0.0
        if name in must_haves:
            skill_score += 10.0
        elif name in nice_to_haves:
            skill_score += 5.0
        else:
            continue
            
        # 1. Proficiency bonus (+2.0 points for advanced or expert proficiency)
        if proficiency in ["advanced", "expert"]:
            skill_score += 2.0
            
        # 2. Endorsements bonus (+0.1 points per endorsement, capped at 3.0 points)
        if endorsements > 0:
            endorsements_bonus = endorsements * 0.1
            skill_score += min(endorsements_bonus, 3.0)
            
        # 3. Duration bonus: 0.25 points per year (12 months), capped at 2.0 points
        if duration > 0:
            duration_bonus = (duration / 12.0) * 0.25
            skill_score += min(duration_bonus, 2.0)
            
        score += skill_score
        
    return score


def score_experience(candidate: Dict[str, Any]) -> float:
    """
    Score candidate experience:
    - Ideal range is 5-9 years (highest score).
    - Medium score for 3-5 years or 9-12 years.
    - Lower score otherwise.
    """
    profile = candidate.get("profile", {})
    experience = profile.get("years_of_experience")
    if experience is None:
        experience = 0.0
            
    if IDEAL_MIN_EXPERIENCE <= experience <= IDEAL_MAX_EXPERIENCE:
        return 100.0

    elif 3.0 <= experience < IDEAL_MIN_EXPERIENCE:
        return 35.0

    elif IDEAL_MAX_EXPERIENCE < experience <= 12.0:
        return 75.0

    elif experience > 12.0:
        return 50.0

    else:
        return 20.0


def score_behavior(candidate: Dict[str, Any]) -> float:
    """
    Score behavior signals from redrob_signals.
    Reward:
      - open_to_work_flag
      - recruiter_response_rate
      - github_activity_score
      - interview_completion_rate
      - profile_completeness_score
      - saved_by_recruiters_30d
      - verified_email
      - verified_phone
      - linkedin_connected
    Penalize:
      - notice_period_days > 90
      - very low recruiter_response_rate
      - poor activity signals
    """
    score = 0.0
    signals = candidate.get("redrob_signals", {})
    if not signals:
        return score

    # 1. Open to work flag
    if signals.get("open_to_work_flag", False):
        score += 8.0

    # 2. Recruiter response rate
    response_rate = signals.get("recruiter_response_rate")
    if response_rate is not None:
        if response_rate >= 0.8:
            score += 15.0
        elif response_rate >= 0.5:
            score += 10.0
        elif response_rate >= 0.3:
            score += 5.0
        elif response_rate < 0.2:
            score -= 10.0

    # 3. GitHub activity score
    github_score = signals.get("github_activity_score")
    if github_score is None:
        github_score = -1
    if github_score > -1:
        if github_score >= 80:
            score += 15.0
        elif github_score >= 50:
            score += 10.0
        elif github_score >= 20:
            score += 5.0

    # 4. Interview completion rate
    interview_rate = signals.get("interview_completion_rate")
    if interview_rate is not None:
        if interview_rate >= 0.8:
            score += 10.0
        elif interview_rate >= 0.5:
            score += 5.0
        elif interview_rate < 0.3:
            score -= 5.0

    # 5. Profile completeness score
    completeness = signals.get("profile_completeness_score")
    if completeness is not None:
        if completeness >= 80.0:
            score += 8.0
        elif completeness >= 50.0:
            score += 4.0
        elif completeness < 30.0:
            score -= 5.0

    # 6. Saved by recruiters 30d
    saved_count = signals.get("saved_by_recruiters_30d")
    if saved_count is not None:
        if saved_count >= 10:
            score += 10.0
        elif saved_count >= 5:
            score += 5.0
        elif saved_count >= 1:
            score += 2.0

    # 7. Verified email and phone
    if signals.get("verified_email", False):
        score += 3.0
    if signals.get("verified_phone", False):
        score += 3.0

    # 8. LinkedIn connected
    if signals.get("linkedin_connected", False):
        score += 4.0

    # 9. Notice period (penalize if > 90)
    notice_period = signals.get("notice_period_days")
    if notice_period is None:
        notice_period = 180
    if notice_period > 90:
        score -= 15.0
    elif notice_period <= 30:
        # short notice period bonus
        score += 5.0

    # 10. Poor activity signals or unverified profile penalty
    if not signals.get("verified_email", False) and not signals.get("verified_phone", False):
        score -= 5.0
    
    views = signals.get("profile_views_received_30d")
    if views is not None and views <= 1:
        score -= 3.0

    return score


def score_location(candidate: Dict[str, Any]) -> float:
    """
    Score candidate location preferences:
    - Reward India
    - Reward Preferred locations from PREFERRED_LOCATIONS
    - Reward Willingness to relocate
    - Reward Flexible work preferences (hybrid, flexible)
    """
    score = 0.0
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})

    country = (profile.get("country") or "").lower().strip()
    location = (profile.get("location") or "").lower().strip()

    # 1. Reward India
    if country == "india":
        score += 40.0

    # 2. Reward preferred locations
    for pref in PREFERRED_LOCATIONS:
        if pref.lower().strip() in location:
            score += 30.0
            break

    # 3. Reward willing to relocate
    if signals.get("willing_to_relocate", False):
        score += 20.0

    # 4. Reward flexible work preferences (hybrid or flexible work modes)
    pref_mode = (signals.get("preferred_work_mode") or "").lower().strip()
    if pref_mode in ["hybrid", "flexible"]:
        score += 10.0

    return min(score, 100.0)


def score_penalties(candidate: Dict[str, Any]) -> float:
    """
    Score negative penalties.
    - Penalize negative keywords in candidate text.
    - Penalize consulting current company.
    - Penalize obvious non-AI roles (marketing, HR, accountant, sales, 
      civil engineer, mechanical engineer, customer support, operations manager).
    - Do NOT over-penalize candidates with strong AI skills (reduce penalties by 50%).
    """
    raw_penalty = 0.0
    profile = candidate.get("profile", {})

    # 1. Negative keywords in combined profile text
    text = build_candidate_text(candidate).lower()
    for kw in NEGATIVE_KEYWORDS:
        kw_lower = kw.lower().strip()
        if kw_lower in text:
            raw_penalty += 10.0

    # 2. Consulting current company
    current_company = (profile.get("current_company") or "").lower().strip()
    consulting_companies_lower = {c.lower().strip() for c in CONSULTING_COMPANIES}
    if current_company in consulting_companies_lower:
        raw_penalty += 15.0

    # 3. Obvious non-AI roles in current title or headline
    current_title = (profile.get("current_title") or "").lower().strip()
    non_ai_keywords = [
        "marketing", "hr", "human resources", "recruiter", "accountant",
        "accounting", "sales", "civil engineer", "mechanical engineer",
        "customer support", "customer success", "support representative",
        "operations manager"
    ]
    
    seniority_penalty_keywords = [
    "junior",
    "intern",
    "trainee",
    "associate"
    ]

    if any(kw in current_title for kw in seniority_penalty_keywords):
        raw_penalty += 20.0
        
    if any(kw in current_title for kw in non_ai_keywords):
        raw_penalty += 25.0

    headline = (profile.get("headline") or "").lower()
    if any(kw in headline for kw in non_ai_keywords):
        raw_penalty += 10.0

    # 4. Mitigation check: strong AI/retrieval skills
    must_have_count = 0
    has_advanced_must_have = False
    must_haves = {s.lower().strip() for s in MUST_HAVE_SKILLS}
    
    for skill in candidate.get("skills", []):
        if isinstance(skill, dict):
            name = (skill.get("name") or "").lower().strip()
            prof = (skill.get("proficiency") or "").lower().strip()
        else:
            name = str(skill or "").lower().strip()
            prof = ""
            
        if name in must_haves:
            must_have_count += 1
            if prof in ["advanced", "expert"]:
                has_advanced_must_have = True

    # Strong AI criteria: >= 3 must-have skills OR (>= 1 must-have skill with advanced/expert proficiency)
    has_strong_ai = (must_have_count >= 3) or (must_have_count >= 1 and has_advanced_must_have)

    if has_strong_ai:
        # Scale down penalty by 50%
        final_penalty = raw_penalty * 0.5
    else:
        final_penalty = raw_penalty

    # Return penalties as a negative score
    return max(-final_penalty, -60.0)


def get_score_breakdown(candidate: Dict[str, Any]) -> Dict[str, float]:
    """
    Return a breakdown of all scoring components.
    """
    return {
        "skills_score": score_skills(candidate),
        "experience_score": score_experience(candidate),
        "behavior_score": score_behavior(candidate),
        "location_score": score_location(candidate),
        "penalty_score": score_penalties(candidate)
    }


def normalize_score(value: float, max_value: float) -> float:
    """
    Return score normalized to 0-100.
    """
    if max_value <= 0:
        return 0.0
    return (value / max_value) * 100.0


if __name__ == "__main__":
    # Test block: load first 5 candidates and print their score breakdowns
    print("Loading test candidates...")
    candidates = load_candidates(limit=5)
    
    print("\nCandidate Scoring Breakdown Test:")
    print("=" * 60)
    for i, candidate in enumerate(candidates, 1):
        cid = candidate.get("candidate_id", f"UNKNOWN_{i}")
        breakdown = get_score_breakdown(candidate)
        
        print(f"Candidate ID: {cid}")
        print(f"Skills Score: {breakdown['skills_score']:.2f}")
        print(f"Experience Score: {breakdown['experience_score']:.2f}")
        print(f"Behavior Score: {breakdown['behavior_score']:.2f}")
        print(f"Location Score: {breakdown['location_score']:.2f}")
        print(f"Penalty Score: {breakdown['penalty_score']:.2f}")
        print(f"Score Breakdown: {breakdown}")
        print("-" * 40)
    print("=" * 60)
