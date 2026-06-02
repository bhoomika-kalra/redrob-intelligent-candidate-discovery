import csv
import json
import faiss
import numpy as np
from docx import Document
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from career_intelligence import score_career_fit
from retrieval_intelligence import score_retrieval_intelligence

from load_candidates import load_candidates
from scoring import get_score_breakdown
from reasoning import generate_reasoning

INDEX_PATH = "outputs/faiss_index.index"
IDS_PATH = "outputs/candidate_ids.json"
OUTPUT_PATH = "outputs/final_submission.csv"

TOP_K = 1000


def read_job_description():
    doc = Document("data/job_description.docx")
    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text


def load_candidate_map():
    candidate_map = {}

    candidates = load_candidates()

    for candidate in candidates:
        candidate_map[candidate["candidate_id"]] = candidate

    return candidate_map


def calculate_final_score(semantic_score, breakdown):
    final_score = (
    0.25 * semantic_score
    + 0.12 * breakdown["skills_score"]
    + 0.08 * breakdown["retrieval_ranking_score"]
    + 0.20 * breakdown["career_fit_score"]
    + 0.15 * breakdown["retrieval_intelligence_score"]
    + 0.12 * breakdown["experience_score"]
    + 0.05 * breakdown["behavior_score"]
    + 0.03 * breakdown["location_score"]
    + breakdown["penalty_score"]
)

    return round(final_score, 4)


def main():
    print("Loading model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Reading job description...")
    jd_text = read_job_description()

    print("Creating JD embedding...")
    jd_embedding = model.encode(
        [jd_text],
        normalize_embeddings=True
    ).astype("float32")

    print("Loading FAISS index...")
    index = faiss.read_index(INDEX_PATH)

    print("Loading candidate IDs...")
    with open(IDS_PATH, "r", encoding="utf-8") as f:
        candidate_ids = json.load(f)

    print("Searching top candidates from FAISS...")
    scores, indices = index.search(jd_embedding, TOP_K)

    print("Loading full candidate data...")
    candidate_map = load_candidate_map()

    ranked_results = []

    print("Reranking candidates...")
    for position, idx in enumerate(tqdm(indices[0])):
        candidate_id = candidate_ids[idx]
        candidate = candidate_map.get(candidate_id)

        if candidate is None:
            continue

        semantic_score = float(scores[0][position]) * 100
        breakdown = get_score_breakdown(candidate)
        breakdown["career_fit_score"] = score_career_fit(candidate)
        breakdown["retrieval_intelligence_score"] = score_retrieval_intelligence(candidate)
        final_score = calculate_final_score(semantic_score, breakdown)
        experience = candidate.get("profile", {}).get("years_of_experience", 0)
        career_score = breakdown.get("career_fit_score", 0)
        retrieval_score = breakdown.get("retrieval_intelligence_score", 0)

        if experience < 4:
            final_score -= 15
        elif experience < 5:
            final_score -= 8

        if retrieval_score < 30 and career_score < 60:
            final_score -= 6
        reasoning = generate_reasoning(candidate, breakdown)

        ranked_results.append({
            "candidate_id": candidate_id,
            "score": final_score,
            "reasoning": reasoning,
            "breakdown": breakdown,
            "semantic_score": round(semantic_score, 2)
        })

    ranked_results.sort(key=lambda x: x["score"], reverse=True)

    top_100 = ranked_results[:100]

    print("Writing final submission CSV...")
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])

        for rank, row in enumerate(top_100, start=1):
            writer.writerow([
                row["candidate_id"],
                rank,
                row["score"],
                row["reasoning"]
            ])

    print("\nFinal submission created:")
    print(OUTPUT_PATH)

    print("\nTOP 10 FINAL CANDIDATES\n")
    for i, row in enumerate(top_100[:10], start=1):
        candidate = candidate_map[row["candidate_id"]]
        profile = candidate.get("profile", {})

        print(
            f"\n{i}. {row['candidate_id']}"
        )

        print(
            f"Title: {profile.get('current_title', 'NA')}"
        )

        print(
            f"Experience: {profile.get('years_of_experience', 0)}"
        )

        print(
            f"Final Score: {row['score']}"
        )

        print(
            f"Semantic Score: {row['semantic_score']}"
        )

        print(
            f"Reasoning: {row['reasoning']}"
        )


if __name__ == "__main__":
    main()