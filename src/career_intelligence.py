from load_candidates import load_candidates


AI_ML_TITLES = [
    "ai engineer",
    "senior ai engineer",
    "ml engineer",
    "machine learning engineer",
    "senior software engineer (ml)",
    "ai research engineer",
    "applied scientist",
    "data scientist",
    "nlp engineer",
    "search engineer",
    "recommendation engineer",
]

SEARCH_RANKING_KEYWORDS = [
    "search",
    "retrieval",
    "ranking",
    "recommendation",
    "recommender",
    "matching",
    "personalization",
    "semantic search",
    "vector search",
    "bm25",
    "faiss",
    "milvus",
    "qdrant",
    "pinecone",
    "weaviate",
    "elasticsearch",
    "opensearch",
]

PRODUCT_KEYWORDS = [
    "product",
    "saas",
    "platform",
    "marketplace",
    "users",
    "customer",
    "production",
    "deployed",
    "scale",
]

NEGATIVE_CAREER_TITLES = [
    "project manager",
    "business analyst",
    "marketing manager",
    "hr manager",
    "accountant",
    "sales",
    "customer support",
    "operations manager",
    "civil engineer",
    "mechanical engineer",
    "graphic designer",
    "content writer",
    "seo",
    "designer",
    "copywriter",
    "social media",
]


def score_career_fit(candidate):
    score = 0.0

    profile = candidate.get("profile", {})
    career_history = candidate.get("career_history", [])

    current_title = profile.get("current_title", "").lower()
    headline = profile.get("headline", "").lower()
    summary = profile.get("summary", "").lower()

    combined_text = f"{current_title} {headline} {summary}".lower()

    # Current title fit
    for title in AI_ML_TITLES:
        if title in current_title or title in headline:
            score += 30
            break

    # Search / ranking / recommendation evidence
    for keyword in SEARCH_RANKING_KEYWORDS:
        if keyword in combined_text:
            score += 6

    # Career history evidence
    for job in career_history:
        job_title = job.get("title", "").lower()
        description = job.get("description", "").lower()
        industry = job.get("industry", "").lower()

        job_text = f"{job_title} {description} {industry}"

        for title in AI_ML_TITLES:
            if title in job_title:
                score += 12
                break

        for keyword in SEARCH_RANKING_KEYWORDS:
            if keyword in job_text:
                score += 5

        for keyword in PRODUCT_KEYWORDS:
            if keyword in job_text:
                score += 3

    # Penalize non-engineering career direction
    for bad_title in NEGATIVE_CAREER_TITLES:
        if bad_title in current_title:
            score -= 60

    # Reward seniority
    if "senior" in current_title:
        score += 10
        
    junior_keywords = ["junior", "intern", "trainee", "associate"]

    if any(keyword in current_title for keyword in junior_keywords):
        score -= 60

    # Reward clear engineering background
    if "engineer" in current_title:
        score += 10

    return max(0.0, min(score, 100.0))


if __name__ == "__main__":
    candidates = load_candidates(limit=1000)

    for candidate in candidates:
        score = score_career_fit(candidate)

        if score > 40:
            print(
                candidate["candidate_id"],
                candidate["profile"].get("current_title", ""),
                score
            )