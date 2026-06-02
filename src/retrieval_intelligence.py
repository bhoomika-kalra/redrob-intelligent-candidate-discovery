from load_candidates import load_candidates


STRONG_RETRIEVAL_TERMS = [
    "faiss",
    "qdrant",
    "milvus",
    "pinecone",
    "weaviate",
    "elasticsearch",
    "opensearch",
    "vector search",
    "semantic search",
    "dense retrieval",
    "hybrid search",
    "retrieval augmented generation",
    "rag",
    "learning to rank",
    "ltr",
    "recommendation systems",
    "recommender systems",
    "embeddings",
    "sentence transformers",
]

VECTOR_DB_TERMS = [
    "faiss",
    "milvus",
    "qdrant",
    "pinecone",
    "weaviate",
    "elasticsearch",
    "opensearch",
]

# PRODUCTION_TERMS = [
#     "deployed",
#     "production",
#     "real users",
#     "scale",
#     "latency",
#     "index refresh",
#     "a/b testing",
#     "ndcg",
#     "mrr",
#     "map",
#     "offline evaluation",
#     "online evaluation",
# ]

WEAK_AI_TERMS = [
    "chatgpt",
    "prompt engineering",
    "langchain tutorial",
    "demo app",
]


def build_retrieval_text(candidate):
    profile = candidate.get("profile", {})
    career_history = candidate.get("career_history", [])
    skills = candidate.get("skills", [])

    parts = [
        profile.get("headline", ""),
        profile.get("summary", ""),
        profile.get("current_title", ""),
    ]

    for job in career_history:
        parts.append(job.get("title", ""))
        parts.append(job.get("description", ""))
        parts.append(job.get("industry", ""))

    for skill in skills:
        if isinstance(skill, dict):
            parts.append(skill.get("name", ""))

    return " ".join(parts).lower()


def score_retrieval_intelligence(candidate):
    score = 0.0
    text = build_retrieval_text(candidate)
    profile = candidate.get("profile", {})
    current_title = profile.get("current_title", "").lower()

    allowed_title_keywords = [
        "ai",
        "ml",
        "machine learning",
        "data scientist",
        "data engineer",
        "software engineer",
        "research engineer",
        "search engineer",
        "recommendation",
        "backend engineer",
        "analytics engineer",
    ]

    if not any(keyword in current_title for keyword in allowed_title_keywords):
        return 0.0
    
    positive_titles = [
        "ai",
        "ml",
        "machine learning",
        "data scientist",
        "research engineer",
        "search engineer",
        "recommendation",
    ]

    negative_titles = [
        "graphic designer",
        "content writer",
        "seo",
        "marketing",
        "hr",
        "accountant",
        "civil engineer",
        "mechanical engineer",
        "project manager",
        "business analyst",
    ]

    for term in STRONG_RETRIEVAL_TERMS:
        if term in text:
            score += 12

    for term in VECTOR_DB_TERMS:
        if term in text:
            score += 7

    for term in WEAK_AI_TERMS:
        if term in text:
            score -= 6

    if any(t in current_title for t in positive_titles):
        score += 20

    if any(t in current_title for t in negative_titles):
        score -= 50

    return max(0.0, min(score, 100.0))


if __name__ == "__main__":
    candidates = load_candidates(limit=1000)

    results = []

    for candidate in candidates:
        score = score_retrieval_intelligence(candidate)
        results.append((
            score,
            candidate["candidate_id"],
            candidate["profile"].get("current_title", "")
        ))

    results.sort(reverse=True)

    print("\nTOP RETRIEVAL INTELLIGENCE SCORES\n")

    for row in results[:20]:
        print(row)