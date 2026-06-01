import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from docx import Document

print("Loading model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Model loaded successfully.\n")


# -------------------------
# Read Job Description
# -------------------------

doc = Document("data/job_description.docx")

jd_text = ""

for para in doc.paragraphs:
    jd_text += para.text + "\n"

print("JD loaded.\n")


# -------------------------
# Load Candidates
# -------------------------

with open(
    "data/sample_candidates.json",
    "r",
    encoding="utf-8"
) as f:
    candidates = json.load(f)

print("Candidates loaded.\n")


# -------------------------
# Create JD Embedding
# -------------------------

jd_embedding = model.encode(jd_text)


# -------------------------
# Candidate Similarity
# -------------------------

results = []

for candidate in candidates:

    profile = candidate.get("profile", {})

    text = ""

    text += profile.get("headline", "") + " "
    text += profile.get("summary", "") + " "
    text += profile.get("current_title", "") + " "

    for skill in candidate.get("skills", []):

        if isinstance(skill, dict):
            text += skill.get("name", "") + " "

    candidate_embedding = model.encode(text)

    similarity = cosine_similarity(
        [jd_embedding],
        [candidate_embedding]
    )[0][0]

    results.append({
        "candidate_id": candidate["candidate_id"],
        "semantic_score": round(float(similarity * 100), 2)
    })


# -------------------------
# Sort Results
# -------------------------

results.sort(
    key=lambda x: x["semantic_score"],
    reverse=True
)

print("\nTOP 10 SEMANTIC MATCHES\n")

for i, row in enumerate(results[:10], start=1):

    print(
        f"{i}. "
        f"{row['candidate_id']} "
        f"-> Semantic Score: "
        f"{row['semantic_score']}"
    )