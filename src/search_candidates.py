import json
import faiss
import numpy as np
from docx import Document
from sentence_transformers import SentenceTransformer

INDEX_PATH = "outputs/faiss_index.index"
IDS_PATH = "outputs/candidate_ids.json"
TOP_K = 20


def read_job_description():
    doc = Document("data/job_description.docx")
    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text


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

    print("Searching candidates...")
    scores, indices = index.search(jd_embedding, TOP_K)

    print("\nTOP SEMANTIC CANDIDATES FROM FAISS\n")

    for rank, idx in enumerate(indices[0], start=1):
        candidate_id = candidate_ids[idx]
        score = float(scores[0][rank - 1])

        print(
            f"{rank}. {candidate_id} "
            f"-> Similarity Score: {round(score * 100, 2)}"
        )


if __name__ == "__main__":
    main()